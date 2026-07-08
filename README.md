# Fizard Plugins

Plugins and agent skills by [Fizard](https://fizard.com) — for Claude Code,
Codex, and any agent that speaks the open Agent Skills format. Install once,
then get every update automatically (or with one command).

## Install

### Claude Code

```
/plugin marketplace add fizard/fizard-plugins
/plugin install qonto-matchmaker@fizard
```

To receive updates automatically: `/plugin` → **Marketplaces** tab →
select `fizard` → **Enable auto-update**. Or update manually any time with
`/plugin marketplace update fizard`.

**Using the desktop app?** The `/plugin` command is terminal-only. Run the
same thing once in any terminal instead — the plugin is then available
everywhere, including the desktop app (new sessions):

```bash
claude plugin marketplace add fizard/fizard-plugins
claude plugin install qonto-matchmaker@fizard
```

### Codex

```
codex plugin marketplace add fizard/fizard-plugins
```

Then open `/plugins` in Codex, find **Fizard**, and install `qonto-matchmaker`.

### Cursor and other agents (skill only)

```
npx skills add fizard/fizard-plugins
```

The [skills CLI](https://github.com/vercel-labs/skills) detects your
installed agents and puts the skill where each expects it. Update any time
with `npx skills update`.

## Plugins

### Qonto Matchmaker by Fizard (`qonto-matchmaker`)

The matchmaker between your inbox and your bank account: finds Qonto
transactions with missing receipts, matches invoice PDFs from your email
inbox against them (exact amount, vendor, date — and only when the match
is unambiguous), attaches confident matches automatically via the Qonto
MCP, and ends every run with a progress report: what's done, what's
missing, where to find the rest. Each run ends with an audit of the
receipts already attached — wrong ones get replaced or removed, each
only with your approval.

Fair warning: it has a personality, and his name is **Merlin**. Think
best friend with a mission — he makes receipt-chasing fun, doesn't mince
words when receipts sit open for months, and celebrates you when the
month is clean. All in service of one goal: books your accountant can
close without a single follow-up question.

**Qonto connection is bundled:** the plugin ships the Qonto MCP server
config (`https://mcp.qonto.com/mcp`); on first use you just log in to Qonto
once (Claude Code: `/mcp` → qonto → authenticate). Already using the Qonto
MCP? Nothing changes — the bundled config is deduplicated against your
existing connection, which keeps working as-is.

**Email access you connect yourself**, depending on what you use:

- **Gmail / Google Workspace:** Google's official remote MCP server
  ([setup guide](https://developers.google.com/workspace/gmail/api/guides/configure-mcp-server)
  — requires a Google Cloud project and OAuth client, one-time admin setup).
- **Outlook / Microsoft 365:** e.g. the community
  [ms-365-mcp-server](https://github.com/softeria/ms-365-mcp-server)
  (`claude mcp add ms365 -- npx -y @softeria/ms-365-mcp-server`).

**Optional, recommended: browser access.** Some receipts never arrive as
email attachments (Stripe receipt links, portal downloads from Google,
Apple, …). With the [Claude in Chrome](https://claude.ai/chrome) extension
connected (Codex: the built-in **Chrome** plugin plus the Codex Chrome
Extension), the matchmaker offers to download those straight from the
vendor portal — you handle the login, it handles the rest. Without it
they stay a manual download.

**Getting started:** run `/reconcile-invoices <Monat>` (e.g.
`/reconcile-invoices Juni` — the month is always read in the current year)
or just ask *"Wo fehlen Belege?"*. On first use (or whenever a connection
is missing) Merlin runs the onboarding first: email connector, Qonto
connection, optional browser setup.

## Feedback

Ideas and improvement suggestions are always welcome — send them to
[marc@fizard.com](mailto:marc@fizard.com). Or just tell Merlin: if your
connected mailbox can send mail, he'll compose the message for you and
send it once you've approved the text.

## Release workflow (Fizard-internal)

1. Update skill content under `plugins/<plugin>/skills/`.
2. Bump the version (scheme `YEAR.MONTH.PATCH`) in
   `plugins/<plugin>/.codex-plugin/plugin.json` — **only there**. The Claude
   manifests deliberately carry no version: for Claude Code and Cowork every
   commit on `main` *is* a release (the commit SHA becomes the version), while
   Codex caches by manifest version and needs the bump to pick up changes.
3. Add a `CHANGELOG.md` entry under the new Codex version.
4. `claude plugin validate .claude-plugin/marketplace.json`, then commit and
   push to `main`. Claude clients with auto-update get the new state on their
   next start; Codex and skills-CLI clients on their next manual update.

## Structure

```
.claude-plugin/marketplace.json          Claude Code catalog
.agents/plugins/marketplace.json         Codex catalog
plugins/qonto-matchmaker/
├── .claude-plugin/plugin.json           Claude Code manifest + version
├── .codex-plugin/plugin.json            Codex manifest + version
├── .mcp.json                            bundled Qonto MCP server config
└── skills/
    ├── fizard-onboard/SKILL.md          onboarding flow
    └── reconcile-invoices/SKILL.md      the monthly reconciliation
CHANGELOG.md                             what changed per release
```

Both plugin systems expect `skills/` at the plugin root, so a single plugin
directory carries both manifests and one shared set of skills. New plugins
get their own `plugins/<name>/` directory plus an entry in **both** catalogs.
