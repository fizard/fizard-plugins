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
`/plugin marketplace update fizard`. Auto-update refreshes the catalog in
the background; if a session still reports an older installed version —
the skill's self-update check watches for exactly this — bring it current
with `claude plugin update qonto-matchmaker@fizard`.

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

The matchmaker between your inbox and your bank account: it finds Qonto
transactions with missing receipts, matches invoice PDFs from your
email against them (exact amount, vendor, date — and only when the
match is unambiguous), and attaches confident matches via the Qonto MCP
after one bulk confirmation. Every run ends with a progress report:
what's done, what's missing (and whose card it was), where to find the
rest. On request it also audits the receipts already attached — fixes
only with your approval.

*Qonto Matchmaker is an independent Fizard product — not affiliated with
or endorsed by Qonto.*

**Qonto connection is bundled:** the plugin ships the Qonto MCP server
config (`https://mcp.qonto.com/mcp`); on first use you just log in to Qonto
once (Claude Code: `/mcp` → qonto → authenticate). Already using the Qonto
MCP — your own server entry or the claude.ai connector? It keeps working
as-is: the bundled server runs alongside it, and the skills use whichever
Qonto connection is authenticated (preferring the bundled one).

**Email access you connect yourself**, depending on what you use:

- **Gmail / Google Workspace:** Google's official remote MCP server
  ([setup guide](https://developers.google.com/workspace/gmail/api/guides/configure-mcp-server)
  — requires a Google Cloud project and OAuth client, one-time admin setup).
- **Outlook / Microsoft 365:** e.g. the community
  [ms-365-mcp-server](https://github.com/softeria/ms-365-mcp-server)
  (`claude mcp add ms365 -- npx -y @softeria/ms-365-mcp-server`).

**Optional: browser access.** Some receipts never arrive as email
attachments (Stripe receipt links, portal downloads from Google, Apple,
…). The matchmaker itself deliberately sticks to your inboxes — but a
dedicated portal-download skill is on its way. Connecting the browser
now ([Claude in Chrome](https://claude.ai/chrome); Codex: the built-in
**Chrome** plugin plus the Codex Chrome Extension) means it's ready the
moment that ships.

**Getting started:** run `/reconcile-invoices <Monat>` (e.g.
`/reconcile-invoices Juni` — the month is always read in the current year)
or just ask *"Wo fehlen Belege?"*. On first use (or whenever a connection
is missing) the onboarding runs first: Qonto connection, email connector,
optional browser setup.

## Feedback

Ideas and improvement suggestions are always welcome — send them to
[marc@fizard.com](mailto:marc@fizard.com), or hand them over in a
session: if your connected mailbox can send mail, the plugin composes
the message for you and sends it once you've approved the text.

## Release workflow (Fizard-internal)

1. Update skill content under `plugins/<plugin>/skills/`.
2. Bump the version (scheme `YEAR.MONTH.PATCH`) in
   `plugins/<plugin>/.codex-plugin/plugin.json` — **only there**. The Claude
   manifests deliberately carry no version: for Claude Code and Cowork every
   commit on `main` *is* a release (the commit SHA becomes the version), while
   Codex caches by manifest version and needs the bump to pick up changes.
3. Add a `CHANGELOG.md` entry under the new Codex version.
4. `claude plugin validate .claude-plugin/marketplace.json`, then commit and
   push to `main` — CI re-runs the validation and checks that the Codex
   manifest version matches the changelog head. Claude clients with
   auto-update get the new state on their next start; Codex and skills-CLI
   clients on their next manual update.

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
.github/workflows/validate.yml           CI: manifest validation + version check
```

Both plugin systems expect `skills/` at the plugin root, so a single plugin
directory carries both manifests and one shared set of skills. New plugins
get their own `plugins/<name>/` directory plus an entry in **both** catalogs.
