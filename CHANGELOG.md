# Changelog

Versions follow the Codex manifest (`.codex-plugin/plugin.json`). Claude
Code and Cowork update per commit — their installed "version" is the git
commit SHA.

## 2026.7.14 — July 2026

- **The attachment audit now runs before the matching** (step 3 of 9):
  wrong attachments are caught first, the affected transactions join the
  mailbox search, and Merlin hunts the correct invoice himself — the
  proposed swap appears in the same validation overview and runs with
  the same single confirmation. Removing without a replacement still
  takes its own explicit approval. The fix costs the user one decision,
  not one errand.
- **Working principle, now in writing:** as little work for the user as
  possible, as much as necessary — Merlin does the legwork, the user
  only decides.
- **Cheer through the whole journey:** Merlin's good mood carries the
  user through the chore — progress is named the moment it happens, the
  numbers tick upward mid-run ("12 of 15 already home"), and the
  onboarding counts its steps down. The user should leave every run in
  a better mood than they came.

## 2026.7.13 — July 2026

- **Attachment audit as the final step:** every standard run now ends by
  verifying the receipts that are already attached — same criteria,
  opposite direction. Wrong ones get replaced or removed only with the
  user's explicit approval; scheduled runs only report. Also available
  standalone ("prüfe die hochgeladenen Belege", "audit receipts").
- **Roadmap opener:** Merlin starts each run with the short version of
  the journey — step by step, finished month at the end — and calls out
  the stations as he passes them.
- **Explicit browser checks per surface:** onboarding and the portal step
  now look for the exact integration by name — **Claude in Chrome** on
  Claude surfaces (lookalike MCPs don't count), the built-in **Chrome**
  plugin with the **Codex Chrome Extension** on Codex; a Chrome DevTools
  MCP stays the fallback for other agents. When offering it, Merlin
  explains capability and boundary: passwords never pass through him —
  the user logs in, he only drives the already-open session.
- **Tool gate before every step:** each workflow step first verifies that
  the tool it needs is available and authenticated right now (cheap probe
  calls when in doubt) — never run a step against a missing tool, never
  fake its result.
- Codex prompt cards reordered: "Set me up" now comes first.

## 2026.7.12 — July 2026

- **Meet Merlin.** The plugin now speaks with one voice: Merlin, the
  user's best friend with a mission — every receipt uploaded so the
  accountant can close the books without a single follow-up question. He
  challenges, praises only what's earned, asks what to call you (unless
  he already knows), and always mirrors your language. Humor never
  weakens a rule.
- **New reconcile flow with a confirmation gate:** scope (month + who's
  asking) → open Qonto transactions (card holders captured) → parallel
  mailbox search → strict five-criteria matching (amount, merchant-aware
  vendor, date, document type, uniqueness) → compact validation
  overview — nothing uploads until the user confirms — then uploads run
  parallel to the missing-receipts overview, grouped by card holder
  (yours / no assignment / per colleague). Unclear cases are asked, never
  guessed.
- **Portal-download phase:** after the upload, Merlin re-offers browser
  access (Chrome MCP preferred, incl. the Claude in Chrome extension) and
  fetches portal-only invoices himself, with live progress updates.
- **Gamification:** every report opens with a month-progress bar
  (`▓▓▓▓▓▓▓▓░░ 12/15 receipts done — 3 to go`); 100% is the win state.
- **Stripe & co. handled precisely:** invoice vs. payment receipt told
  apart by document features; invoice preferred, the receipt attached
  only when no invoice exists (flagged in the report).
- **No-receipt list** formalized and extended: tax offices and municipal
  treasuries, employee payroll, statutory contributions (Krankenkassen,
  Berufsgenossenschaft, Rentenversicherung, KSK, Versorgungswerke),
  payment-provider payouts, internal transfers, Qonto fees — never
  searched, never asked about.
- **Onboarding overhaul:** verifies that *every* mailbox receiving
  invoices is connected and explicitly confirmed (multi-mailbox routes:
  one connection per mailbox, or forwarding/delegation), adds the
  optional browser step, and drops the "Let's Match" / "It's a Match"
  branding.
- **Offboarding:** once nothing more can be uploaded — feedback invitation
  to marc@fizard.com (sent via the connected mailbox after sign-off, when
  it can send) and a scheduled-routine recommendation (rhythm and time of
  day are the user's call; scheduled runs follow the agreed mode).
- **Codex surfaces:** display name **Qonto Matchmaker by Fizard**, website
  fizard.com, three suggested-prompt cards on the plugin page, new skill
  icons (handshake / invoice-check) consolidated to one file per skill at
  a fraction of the download weight.

## 2026.7.11 — July 2026

- Onboarding skill renamed `onboard` → **`fizard-onboard`** (brand-prefixed
  like Anthropic's `smb-onboard`, collision-safe across plugins).

## 2026.7.10 — July 2026

- Setup skill renamed `lets-match` → **`onboard`** (ecosystem convention, cf.
  OpenClaw `onboard` / Anthropic `smb-onboard`); "Let's Match" and
  "It's a Match" remain as branded trigger phrases. Codex display name:
  "Onboarding".
- New generated skill icons (full-bleed, Fizard gradient): plug-and-socket
  with progress dots for onboarding, invoice-with-checkmark for
  reconciliation.

## 2026.7.9 — July 2026

- Per-skill icons for Codex (`agents/openai.yaml` with `icon_small`/
  `icon_large`): a match-heart for "Let's Match", an invoice-with-checkmark
  for "Reconcile Invoices" — both in Fizard brand style.

## 2026.7.8 — July 2026

- Fizard logo added (Codex: `interface.logo`/`composerIcon` + brand color;
  the Claude plugin format has no icon field yet).

## 2026.7.7 — July 2026

- Faster runs: PDF downloads from the inbox and receipt uploads to Qonto now
  run in parallel (concurrent batches of ~5) instead of one-by-one. Failures
  are retried/reported individually without aborting the batch.

## 2026.7.5 — July 2026

- `reconcile-invoices` without a month now always asks which month to
  process before starting (current month suggested, previous month as
  alternative) — it never picks one on its own.

## 2026.7.4 — July 2026

- The self-update check is now surface-aware: it detects whether it runs in
  Claude Code, Cowork/desktop, claude.ai, Codex, or a standalone skill
  install, and offers exactly the matching update command — running it
  directly where a shell is available.

## 2026.7.3 — July 2026

- Self-update check: on each run the skill compares the installed plugin
  version against the repo head and, if outdated, tells the user how to
  update. Best-effort — never blocks the reconciliation.

## 2026.7.2 — July 2026

- New **"Let's Match"** setup skill (triggers: "Let's Match", "It's a
  Match", "Setup"): verifies the email connector — naming an already
  connected one and asking the user to confirm it — then the Qonto
  connection, before handing over to the reconciliation.
- `reconcile-invoices` now takes a **month** argument (name or number, any
  language), always interpreted in the current year.
- Display name is now **Qonto Matchmaker** on all surfaces.
- Repository renamed to `fizard/fizard-plugins`; Claude manifests switched
  to commit-based versioning (every commit is a release for Claude clients).

## 2026.7.1 — July 2026

- Guided first-run setup: if Qonto or email tools are missing, the skill now
  walks the user through connecting them — Qonto via the bundled MCP config
  (terminal) or the Qonto connector on claude.ai/desktop, email via the
  built-in Gmail connector or a Microsoft 365 MCP server.

## 2026.7.0 — July 2026

- First release: **Fizard Qonto Matchmaker** (`qonto-matchmaker`) — matches
  invoice PDFs from your email inbox to Qonto transactions with missing
  receipts and uploads validated matches via the bundled Qonto MCP.
