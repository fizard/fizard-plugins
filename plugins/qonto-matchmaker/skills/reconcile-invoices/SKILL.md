---
name: reconcile-invoices
description: Use when the user wants to reconcile Qonto receipts with invoice emails for a given month — finding Qonto transactions with missing attachments ("fehlende Belege/Rechnungen"), matching invoice PDFs from the email inbox to them, and uploading validated receipts to Qonto via the Qonto MCP. Takes a month as argument (e.g. "reconcile-invoices Juni"), always interpreted in the current year. Trigger on "reconcile receipts", "Belege abgleichen", "wo fehlen Rechnungen", "Rechnungen in Qonto hochladen", or any Qonto attachment/receipt housekeeping.
---

# Fizard Qonto Matchmaker

Match invoice PDFs from the user's email inbox to Qonto transactions that are
missing their receipt, validate each match, and upload it. A wrong receipt on
a transaction is worse than a missing one — it corrupts bookkeeping silently —
so the rules below are deliberately strict: upload only on high confidence,
report everything else for the user to decide.

## Self-update check (best-effort, never blocking)

Once per session, before starting the workflow, check whether this plugin is
outdated. This must never block or delay the reconciliation — on any error
(no network, no shell, unexpected layout) skip silently and continue.

1. **Installed version:** the last path segment of the plugin's install
   directory (the directory this SKILL.md lives in, three levels up) — either
   a git commit SHA prefix (Claude Code / Cowork) or a semver-like string
   (Codex, e.g. `2026.7.2`).
2. **Latest version:**
   - SHA-style → `git ls-remote https://github.com/fizard/fizard-plugins.git HEAD`
     and compare by prefix.
   - Version-style → fetch
     `https://raw.githubusercontent.com/fizard/fizard-plugins/main/plugins/qonto-matchmaker/.codex-plugin/plugin.json`
     and compare the `version` field.
3. **If outdated**, first determine which surface you are running on, then
   act with exactly the one matching command — never list the commands for
   other surfaces. Detect the surface from your own identity and the
   plugin's install path:

   | Surface | How to recognize it | What to do |
   |---|---|---|
   | **Claude Code** (terminal/IDE) | You are Claude with a shell tool; install path under `~/.claude/plugins/` | Offer to run `claude plugin marketplace update fizard && claude plugin update qonto-matchmaker@fizard` yourself, right now. Tell the user it takes effect in the next session. |
   | **Cowork / Claude desktop app** | You are Claude; install path contains `cowork_plugins` or `local-agent-mode-sessions` | No CLI for this — tell the user to sync the fizard-plugins marketplace in Settings → Plugins, or restart the app. |
   | **claude.ai (web)** | You are Claude with no local plugin path | Plugin updates are managed in the plugin/connector settings — point the user there. |
   | **Codex** | You are Codex; plugin loaded from `.codex-plugin`, cache under `~/.codex/` | Offer to run `codex plugin marketplace upgrade fizard` yourself. |
   | **Any other agent** | Skill installed standalone (e.g. via the skills CLI), no plugin manager | Suggest `npx skills update`. |

   Where a shell tool is available, prefer running the update for the user
   (after a short confirmation) over just printing the command. If you
   cannot determine the surface, say an update is available and name the
   repo (`fizard/fizard-plugins`) instead of guessing a command.

If the versions match, say nothing about updates at all.

## Requirements

Before anything else, check that both sides are available: an email tool
that can search mail and download PDF attachments, and the bundled Qonto MCP
tools (authenticated — verify with a cheap probe call like
`get_organization`, not just tool presence). If either is missing or
unauthenticated, switch to the setup flow in the **`lets-match`** skill
("Let's Match") and finish it before starting the workflow. Never simulate
results for a side that isn't connected.

## Month argument

The command takes a **month** (name or number, any language — "Juni", "6",
"June"). The reconciliation window is that calendar month, **always in the
current year** — never a past year, even if the month lies in the future of
today's date; in that case point out that the month hasn't happened yet and
ask what the user meant. If no month is given, ask which month to reconcile
and suggest the current one.

## Modes

- **Dry-run (default):** collect, match, report — upload nothing. Always use
  this on the first run and whenever the user only asks where receipts are
  missing.
- **Apply:** additionally upload high-confidence matches. Only when the user
  explicitly asks ("upload them", "lade hoch").

## Workflow

### 1. Collect invoice candidates from email

Search the inbox (and archive) over the reconciliation window — the
requested month (see "Month argument"), widened by a few days on both sides
since invoices often arrive shortly before or after the charge. Find emails
with PDF attachments that look like invoices or receipts; download the PDFs
to a temp directory.
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
