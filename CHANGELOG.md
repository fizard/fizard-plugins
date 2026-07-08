# Changelog

Versions follow the Codex manifest (`.codex-plugin/plugin.json`). Claude
Code and Cowork update per commit — their installed "version" is the git
commit SHA.

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
