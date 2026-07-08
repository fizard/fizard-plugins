---
name: onboard
description: Onboarding flow for the Qonto Matchmaker. Trigger on "onboard", "setup", "set me up", "get started", the branded phrases "Let's Match" and "It's a Match" in the Qonto/receipts context, on the first use of the plugin, and whenever reconcile-invoices finds a missing or unauthenticated connection. Verifies the email connector and the Qonto connection, confirming with the user which mailbox to use.
---

# Onboarding — Let's Match

Get the user to a working pair of connections — one email source, one Qonto
connection — so `/reconcile-invoices` can run without surprises. Talk to the
user in their language; keep the tone light (it's a matchmaker), but never
skip a verification step.

Run the two checks in order. Don't fail silently on a missing piece — walk
the user through connecting it, one step at a time, then re-check.

Before Step 1, run the **self-update check** described in the sibling
`reconcile-invoices` skill (best-effort, never blocking): if the installed
plugin version is behind the repo, mention it with the matching update
command before continuing the setup.

## Step 1: Email connector

Enumerate the currently available tools that can **search mail and download
PDF attachments** (e.g. the Gmail connector, an Outlook/MS-365 MCP server, or
any other mail-capable MCP).

- **Exactly one found:** tell the user which one it is (by name, e.g. "your
  Gmail connector") and ask whether they're fine using it for the matching —
  or whether they'd rather connect a different mailbox. Only continue after
  they confirm.
- **Several found:** list them and ask which mailbox(es) to use.
- **None found:** ask which provider the user has, then guide them:
  - **Gmail:** on the Claude desktop app / claude.ai, connect the built-in
    **Gmail** connector (Settings → Connectors). For terminal-only setups,
    Google's official remote MCP server needs a one-time Google Cloud setup:
    https://developers.google.com/workspace/gmail/api/guides/configure-mcp-server
  - **Outlook / Microsoft 365:** community MCP server, e.g.
    `claude mcp add ms365 -- npx -y @softeria/ms-365-mcp-server`, then
    authenticate on first use.

After the user reports they connected something, re-check tool availability.
A new connection may require restarting the session — say so if the tools
still don't appear.

## Step 2: Qonto connection

Check that the bundled Qonto MCP tools are available **and authenticated** —
verify with a cheap probe call (e.g. `get_organization`), not just by tool
presence. If unavailable or unauthenticated, give the instruction matching
the user's surface:

- **Claude Code (terminal):** the plugin already bundles the server config —
  run `/mcp`, pick `qonto`, authenticate in the browser.
- **Claude desktop app / claude.ai:** Settings → Connectors
  (claude.ai/settings/connectors) → Browse connectors → search **Qonto** →
  Connect → log in and pick the organization.
- **Codex:** the plugin bundles the server config — run
  `codex mcp login qonto`.

Re-check after the user reports success.

## Step 3: It's a Match!

When both sides verify, close with a short confirmation — "It's a Match!" —
naming the pair that is now connected (mailbox ↔ Qonto organization), and
tell the user how to run the reconciliation from now on:

> `/reconcile-invoices <Monat>` — e.g. `/reconcile-invoices Juni`.
> The month is always interpreted in the current year.

Never simulate results for a side that isn't connected, and never start the
reconciliation workflow from here — hand over to `reconcile-invoices` only
when the user asks for it.
