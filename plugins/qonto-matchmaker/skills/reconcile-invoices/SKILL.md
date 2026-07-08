---
name: reconcile-invoices
description: Use when the user wants to reconcile Qonto receipts with invoice emails — finding Qonto transactions with missing attachments ("fehlende Belege/Rechnungen"), matching invoice PDFs from the email inbox to them, and uploading validated receipts to Qonto via the Qonto MCP. Trigger on "reconcile receipts", "Belege abgleichen", "wo fehlen Rechnungen", "Rechnungen in Qonto hochladen", or any Qonto attachment/receipt housekeeping.
---

# Fizard Qonto Matchmaker

Match invoice PDFs from the user's email inbox to Qonto transactions that are
missing their receipt, validate each match, and upload it. A wrong receipt on
a transaction is worse than a missing one — it corrupts bookkeeping silently —
so the rules below are deliberately strict: upload only on high confidence,
report everything else for the user to decide.

## Requirements and first-run setup

Before anything else, check which tools are available. If something is
missing, don't fail silently — walk the user through connecting it, one step
at a time, then re-check. Only start the workflow when both sides work.

**Qonto** — tools like `list_transactions`, `get_transaction`,
`request_attachment_upload`, `upload_attachment`. If unavailable or
unauthenticated, give the instruction matching the user's surface:

- **Claude Code (terminal):** the plugin already bundles the server config —
  run `/mcp`, pick `qonto`, authenticate in the browser.
- **Claude desktop app / claude.ai:** Settings → Connectors
  (claude.ai/settings/connectors) → Browse connectors → search **Qonto** →
  Connect → log in and pick the organization.
- **Codex:** the plugin bundles the server config — run
  `codex mcp login qonto`.

**Email** — any connected tool that can search mail and download PDF
attachments. If none is available, ask which provider the user has, then:

- **Gmail:** on the Claude desktop app / claude.ai, connect the built-in
  **Gmail** connector (Settings → Connectors). For terminal-only setups,
  Google's official remote MCP server needs a one-time Google Cloud setup:
  https://developers.google.com/workspace/gmail/api/guides/configure-mcp-server
- **Outlook / Microsoft 365:** community MCP server, e.g.
  `claude mcp add ms365 -- npx -y @softeria/ms-365-mcp-server`, then
  authenticate on first use.

After the user reports they connected something, re-check tool availability.
A new connection may require restarting the session — say so if the tools
still don't appear. Never simulate results for a side that isn't connected.

## Modes

- **Dry-run (default):** collect, match, report — upload nothing. Always use
  this on the first run and whenever the user only asks where receipts are
  missing.
- **Apply:** additionally upload high-confidence matches. Only when the user
  explicitly asks ("upload them", "lade hoch").

## Workflow

### 1. Collect invoice candidates from email

Search the inbox (and archive) over the reconciliation window — default the
last 60 days, or the range the user names. Find emails with PDF attachments
that look like invoices or receipts; download the PDFs to a temp directory.
For each PDF, extract: all monetary amounts with currency and surrounding
context, invoice/billing dates, sender address, and subject. If the user has
more than one mailbox connected, collect from all of them and dedupe on the
RFC message id.

### 2. Fetch open transactions from Qonto

`get_organization` for the bank account ids, then `list_transactions` per
account over the same window. A transaction needs a receipt iff
`attachment_required == true` and `attachment_ids` is empty and
`status == "completed"`.

Exclude categories where no third-party invoice exists — they must not eat
candidates: salaries, tax-office and social-insurance debits, transfers
between the user's own Qonto accounts, Qonto's own fees, and
`side == "credit"` income (incoming payments need the user's own outgoing
invoice, not an inbound receipt — count them separately, don't match them).

### 3. Match and validate

For each open transaction, score every candidate PDF:

| Criterion | Rule |
|---|---|
| **Amount** (hard requirement) | A parsed amount equals `amount` in the account currency **or** equals `local_amount` in `local_currency` (card FX: a 13.42 EUR charge may have a 15.60 USD invoice — always check both). Exact to the cent, no tolerance. |
| **Vendor** | Normalized token overlap between transaction `label`/`clean_counterparty_name` and the sender domain/name or PDF text (e.g. `ANTHROPIC* CLAUDE SUB` ↔ `invoicing@anthropic.com`). |
| **Date** | An invoice date within `emitted_at` −14 days … +5 days. Subscriptions usually invoice on the charge day. |

- **High confidence** (upload in apply mode): amount ✓ **and** vendor ✓ **and** date ✓.
- **Review** (report, never auto-upload): amount ✓ but vendor or date fails.
- Duplicate charges (e.g. three identical debits from one vendor on one day):
  assign distinct PDFs 1:1 by closest date; if there are fewer invoices than
  transactions the remainder stays open. Never attach the same PDF to two
  transactions.
- Prefer amounts whose context reads like a total ("Total", "Gesamtbetrag",
  "Amount due") over line items when several candidates tie.
- Stripe-style billing sends an *Invoice* and a *Receipt* PDF for the same
  charge — attach the invoice, drop the receipt.
- Same-price subscriptions match several months' invoices on amount alone.
  Before rating a match high-confidence, confirm the billing period in the
  PDF text matches the charge month; otherwise → review.

### 4. Upload (apply mode only)

Per match, re-check first that the transaction still has no attachment
(`get_transaction`) — the user may have uploaded manually in between. Then:

1. `request_attachment_upload` (file_name, `application/pdf`, size) → `upload_url` + `blob_ref`
2. `curl -sf -X PUT -H "Content-Type: application/pdf" --upload-file <pdf> "<upload_url>"`
3. `upload_attachment` with `blob_ref`, `target: "transaction"`, `transaction_id`

### 5. Report

Always end with this summary, in the user's language:

```
## Reconciliation <date range>
- Open in total: N transactions
- Uploaded / match found: N  (table: date, amount, vendor, PDF)
- Needs review (amount matches, rest doesn't): N, each with the reason
- No candidate found: N  (table + hint where the receipt likely lives:
  vendor portal download, paper receipt for card payments, …)
- Skipped (no receipt required): salaries/tax/internal/income as counts
```

## Known limits

- Link-only receipts (Stripe receipt links, portal-download invoices from
  Google, Apple, and similar) never arrive as PDF attachments — they will
  always land in "no candidate found". Name the vendor portal in the report
  so the user knows where to download manually.
