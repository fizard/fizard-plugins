---
name: fizard-onboard
description: Onboarding flow for the Qonto Matchmaker. Trigger on "onboard", "setup", "set me up", or "get started" when they concern this plugin, Qonto, or receipts (not for unrelated tools), on the first use of the plugin, and whenever reconcile-invoices finds a missing or unauthenticated connection. Checks the Qonto connection first, then verifies that every mailbox receiving invoices is connected and confirmed by the user, then offers optional browser access (Claude in Chrome extension on Claude surfaces, the Chrome plugin with its extension on Codex) for downloading portal-only invoices.
---

# Onboarding

Get the user to a working setup — the Qonto connection plus every
mailbox that receives invoices — and, optionally, browser access for
portal downloads, so `/reconcile-invoices` can run without surprises.

## Language

The user chooses the language — ask, don't guess. When no language is
established yet, the first message includes a quick language choice:
German, English, or whatever else the user prefers. Phrase that first
message itself in the most likely language (what the user wrote —
trigger words like "onboard" or "get started" are commands, not
language indicators), and let the answer settle it. Once chosen — or
already established earlier in the conversation — never ask again: stay
in that language, and switch only when the user asks or clearly
switches themselves.

Run the steps in order. Steps 1 and 2 are required — don't fail silently on
a missing piece; walk the user through connecting it, one step at a time,
then re-check. Step 3 is optional: recommend it, but treat skipping it as a
valid answer, not a failure.

Never defer the work — everything happens right here in the
conversation, now. No parking setup steps for later: not in external
tools (task managers, calendars, note apps — off-limits unless the user
explicitly asks), and not as a vague "we'll finish this another time" —
either complete the step in this session or hand the user the one
concrete action that unblocks it.

Before Step 1, run the **self-update check** described in the sibling
`reconcile-invoices` skill (best-effort, never blocking): if the installed
plugin version is behind the repo, mention it with the matching update
command before continuing the setup.

## Step 1: Qonto connection

Check that a Qonto MCP connection is available **and authenticated** —
the bundled server or one the user already had (own server entry, the
claude.ai Qonto connector). Any counts, duplicates are fine; prefer the
bundled one when several are live. Verify with a cheap probe call (e.g.
`get_organization`), not just by tool presence. If none passes, give
the instruction matching the user's surface:

- **Claude Code (terminal):** the plugin already bundles the server config —
  run `/mcp`, pick `qonto`, authenticate in the browser.
- **Claude desktop app / claude.ai:** Settings → Connectors
  (claude.ai/settings/connectors) → Browse connectors → search **Qonto** →
  Connect → log in and pick the organization.
- **Codex:** the plugin bundles the server config — run
  `codex mcp login qonto`.

Re-check after the user reports success.

## Step 2: Email — all of it

Start by showing what's already there: enumerate the connected tools
that can **search mail and download PDF attachments** (the Gmail
connector, an Outlook/MS-365 MCP server, any other mail-capable MCP)
and name the mailbox(es) they reach. Then get two confirmations
from the user: that this is the mail to work with, and that it is
complete — where do invoices and receipts actually land (shared inboxes
like billing@ or info@, the personal account with old subscriptions,
…)? A mailbox that isn't connected is a receipt the search will never
find.
Map the answers against what's connected:

- **One relevant mailbox:** the built-in Claude or Codex connectors and
  plugins are all it takes. Name the matching tool ("your Gmail
  connector"), double-check that this really is the only place invoices
  arrive, and continue once the user confirms.
- **Several relevant mailboxes:** cover every one of them; the right
  route depends on the setup:
  - **One connection per mailbox** — a second account usually can't live
    inside the same built-in connector, but another mail-capable MCP can
    cover it (e.g. an extra Gmail via Google's MCP server, a second
    MS-365 login via its own server entry).
  - **Consolidate instead** — an auto-forwarding rule or provider-side
    delegation/shared-mailbox access into the already-connected inbox
    works without any extra connector.
  Walk the list mailbox by mailbox until each one is either connected or
  deliberately consolidated — no silent leftovers.
- **None found:** ask which provider the user has, then guide them:
  - **Gmail:** on the Claude desktop app / claude.ai, connect the built-in
    **Gmail** connector (Settings → Connectors). For terminal-only setups,
    Google's official remote MCP server needs a one-time Google Cloud setup:
    https://developers.google.com/workspace/gmail/api/guides/configure-mcp-server
  - **Outlook / Microsoft 365:** community MCP server, e.g.
    `claude mcp add ms365 -- npx -y @softeria/ms-365-mcp-server`, then
    authenticate on first use.
  - On **Codex**, add mail MCPs with `codex mcp add …` instead of
    `claude mcp add …`; the server packages are the same.

After each new connection, re-check tool availability. A new connection
may require restarting the session — say so if the tools still don't
appear. Close the step only when the user has **explicitly confirmed that
every address where invoices arrive is covered** — repeat the final
mailbox list back to them for that confirmation.

## Step 3: Browser access (optional, recommended)

Some receipts never arrive as email attachments — Stripe receipt links,
portal-download invoices from Google, Apple, and similar. Browser
access will let Fizard tooling fetch those straight from the vendor
portals: a dedicated portal-download skill is on its way, and setting
the browser up now means it's ready the moment it ships.

Check **explicitly for the one integration that matches the surface** —
"some browser tool is present" is not enough:

- On **Claude** surfaces: the **Claude in Chrome** tools (the official
  extension-based integration). Similar-sounding Chrome MCPs — e.g.
  "Control Chrome" — are not it and don't replace the extension.
- On **Codex**: the built-in **Chrome** plugin ("Control Chrome with
  Codex") together with its **Codex Chrome Extension**.

If the matching one is connected, name it and move on. If not, **ask the
user explicitly and by name** — and when offering it, explain both what
it enables and where the line is: you can then visit the vendor sites,
drive the browser, and download the invoices yourself — but **passwords
never pass through you**. Logging in stays the user's move, in their own
browser; you only work inside the session that is already open. Say both
halves, then ask whether to set it up now — accepting a "skip"
gracefully:

- **Claude Code (terminal):** needs the **Claude in Chrome** browser
  extension (install via https://claude.ai/chrome) — then run `/chrome`
  in Claude Code and follow the setup to connect it.
- **Claude desktop app / claude.ai:** install the **Claude in Chrome**
  extension from https://claude.ai/chrome and sign in with the same Claude
  account; the browser tools appear once the extension is connected.
- **Codex:** enable the built-in **Chrome** plugin ("Control Chrome with
  Codex", under `/plugins`) and install the **Codex Chrome Extension**
  from its Setup section — it works with the user's existing browser
  logins, exactly what portal downloads need.
- **Any other agent:** a Chrome DevTools MCP is the generic fallback
  (e.g. `npx chrome-devtools-mcp@latest`); depending on setup it may not
  share the user's logged-in sessions.

Re-check after setup; a new connection may require restarting the session.
If the user skips, continue to the wrap-up — portal invoices then simply
remain a manual download.

## Step 4: Wrap-up

When both required sides verify, close with a short confirmation naming
what is now connected (Qonto organization ↔ every mailbox from Step 2,
plus the browser if Step 3 was set up), and tell the user how to run the
reconciliation from now on:

> `/reconcile-invoices <Monat>` — e.g. `/reconcile-invoices Juni`.
> The month is always interpreted in the current year.

End with one short line inviting the user to send improvement suggestions
and ideas to **marc@fizard.com** — they land directly with the maker. If
the email connector verified in Step 2 can send or draft mail, offer to
handle that on the spot: take the user's text, compose the mail, show it,
and send only after they confirm (draft-only tooling: prepare the draft
for them to fire off). Never send without sign-off.

Never simulate results for a side that isn't connected, and never start the
reconciliation workflow from here — hand over to `reconcile-invoices` only
when the user asks for it.
