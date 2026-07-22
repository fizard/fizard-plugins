# Fizard Plugins

Plugins and agent skills by [Fizard](https://fizard.com). Qonto Matchmaker runs
in local Claude Code sessions in the desktop app and CLI, Claude Cowork, and
the Codex app and CLI.

## Install

### Claude Code — desktop app and CLI

The Fizard marketplace is not listed automatically. No repository checkout is
needed.

#### Desktop app (no CLI required)

1. Open the **Code** tab, choose **Local**, and select a local working folder.
   It can be a dedicated empty folder; it does not need to contain this plugin
   repository.
2. Enter these commands one at a time in the session prompt:

   ```text
   /plugin marketplace add fizard/fizard-plugins
   /plugin install qonto-matchmaker@fizard
   ```

3. If Claude asks for the installation scope, choose **User scope**. Then run
   `/reload-plugins`.
4. Open **+ → Plugins** to verify that **Qonto Matchmaker by Fizard** is
   installed.

Claude Code Desktop requires a paid Claude plan. On Windows, Git is required
for local sessions. See Anthropic's [desktop
quickstart](https://code.claude.com/docs/en/desktop-quickstart) and [plugin
installation guide](https://code.claude.com/docs/en/discover-plugins).

#### CLI

Run these commands once in a terminal:

```bash
claude plugin marketplace add fizard/fizard-plugins
claude plugin install qonto-matchmaker@fizard --scope user
```

Start a new session afterward, or run `/reload-plugins` in an open one. With
the scope choice above, both paths install the plugin at user scope, so it is
available to the CLI and local Code-tab sessions on this computer.

To receive updates automatically: `/plugin` → **Marketplaces** tab →
select `fizard` → **Enable auto-update**. For a manual update in the desktop
app, enter:

```text
/plugin marketplace update fizard
/plugin update qonto-matchmaker@fizard
/reload-plugins
```

From the CLI, refresh the catalog and update the plugin:

```bash
claude plugin marketplace update fizard
claude plugin update qonto-matchmaker@fizard
```

Run `/reload-plugins` afterward, or start a new session.

### Claude Cowork — desktop app (no CLI required)

1. Open **Cowork → Customize → Plugins → Browse plugins → Personal**.
2. Select **+ → Add marketplace → Add from a repository**.
3. Enter `https://github.com/fizard/fizard-plugins`.
4. Open **Fizard**, select **Qonto Matchmaker by Fizard**, and choose
   **Install**.
5. Start a new Cowork task and choose **Manually approve**.

Cowork plugins require a paid Claude plan. On Team and Enterprise plans, an
owner must enable both Cowork and Skills. Personal plugins are installed on
the current computer. See Anthropic's [plugin guide for
Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).

Start Qonto work in a Cowork task you open directly with **Manually approve**.
Cowork reads Qonto, creates a missing-receipt report, and validates PDFs you
attach. You then attach the validated file to the named transaction in Qonto.
See Anthropic's [Cowork safety
guidance](https://support.claude.com/en/articles/13364135-use-claude-cowork-safely).

For a manual update, open **Customize → Plugins → Personal → Fizard**, use the
marketplace's **Update** control, update or reinstall Qonto Matchmaker if
prompted, and start a new Cowork task.

### Codex — app and CLI (one-time CLI setup)

The Fizard marketplace is not listed automatically. No repository checkout is
needed. Adding an external Git marketplace currently requires the `codex`
command once, even if you plan to use the plugin in the app. Check that the
installed CLI includes plugin support:

```bash
codex --version
codex plugin --help
```

If either command fails or the `plugin` subcommand is missing, install or
update the [official Codex CLI](https://developers.openai.com/codex/cli). Then
add the marketplace:

```bash
codex plugin marketplace add fizard/fizard-plugins
```

Then choose one path:

- **App:** restart the app, open `/plugins`, find **Fizard**, and install
  `qonto-matchmaker`.
- **CLI:** run `codex plugin add qonto-matchmaker@fizard`.

Start a new task after installing. In the app, verify under
`/plugins` → **Installed** that **Qonto Matchmaker by Fizard** is installed and
enabled. If **Fizard** is missing, run `codex plugin marketplace list`, then
`codex plugin marketplace upgrade fizard`, and restart the app. The installed
plugin is available in the Codex app and CLI.

Codex marketplace updates currently use the terminal. For a manual update,
refresh and reinstall the cached plugin, then start a new task:

```
codex plugin marketplace upgrade fizard
codex plugin add qonto-matchmaker@fizard
```

## Plugins

### Qonto Matchmaker by Fizard (`qonto-matchmaker`)

The matchmaker between your inbox and your bank account: it finds Qonto
transactions with missing receipts. With an attachment-capable mailbox it
matches invoice PDFs using strict checks and attaches only approved,
unambiguous matches via the Qonto MCP; otherwise it provides a report and
manual guidance. Every run ends with what's attached, what's missing (and
whose card it was), and where to find the rest.

*Qonto Matchmaker is an independent Fizard product — not affiliated with
or endorsed by Qonto.*

**Data and permissions:** the plugin itself is instructions plus connector
configuration; it does not send invoice or bank data to a Fizard backend.
Claude Code, Cowork, or Codex and the chosen mail provider process mailbox/PDF
data. Claude Code and Codex upload to Qonto only after you approve the final
mapping in an interactive standard run. In Cowork, you attach each validated
file to Qonto yourself. Downloaded PDFs use a run-specific temporary directory
in the active execution environment. The skill attempts cleanup after a
controlled success, error, or stop; a crash, force-quit, or provider limitation
can prevent it, and provider/session retention still applies. Scheduled runs
and dry-runs produce reports only. Review the permissions and policies of every
connected provider. See the plugin-specific [data and privacy notice](PRIVACY.md);
questions can go to
[privacy@fizard.com](mailto:privacy@fizard.com).

Before an automatic upload, the plugin may read existing PDFs on Qonto
transactions that could compete for the same invoice. It compares only the
fields and hash needed to prevent duplicate use; it does not audit those
existing receipts for accounting correctness.

The official Qonto MCP can expose additional tools allowed by the user's
Qonto role (for example card or invoice operations). The bundled `.mcp.json`
cannot technically allowlist individual tools. Qonto Matchmaker instructs the
agent to use only organization/account/membership/card/transaction reads and
the approved attachment flow; review surface permission prompts and disconnect
or revoke Qonto access when it is no longer needed.

**Qonto connection is bundled:** the plugin ships the Qonto MCP server
config (`https://mcp.qonto.com/mcp`); on first use you log in to Qonto once
(Claude Code: `/mcp` → `qonto` → authenticate; Cowork:
**Customize → Connectors → qonto → Connect**, then enable it through
**+ → Connectors**; Codex: **Settings → MCP servers → qonto → Authenticate**
in the app, or `codex mcp login qonto` in the CLI). [Qonto currently permits MCP
access](https://support-fr.qonto.com/hc/en-us/articles/47588576515089-How-do-I-connect-and-use-the-Qonto-MCP-server)
for Owner, Admin, and Accountant roles. Claude Code may deduplicate connections
to the same endpoint, so an existing Qonto connection can be hidden by the
plugin entry; authenticate the visible `qonto` entry and use that connection
consistently.

**Email access you connect yourself.** Full matching requires a connector
that can search every relevant mailbox, page through all results, and return
the actual bytes of PDF attachments. Seeing a filename or MIME type is not
enough; onboarding verifies this with a harmless test PDF before declaring
the setup ready.

- **Codex:** in the app, open `/plugins`, install and connect the Gmail plugin,
  then start a new task. It qualifies only when `read_attachment` is available
  and the PDF probe succeeds. Use an Outlook integration only when the same
  probe succeeds.
- **Claude Code:** connect an attachment-capable mail MCP that you or your
  organization has reviewed. [Google's official Gmail
  MCP](https://developers.google.com/workspace/gmail/api/reference/mcp)
  currently exposes attachment metadata but not PDF bytes, so it supports a
  missing-receipt report rather than automatic matching and upload.
- **Claude Cowork:** the built-in Gmail connector also exposes only attachment
  metadata, not content. Connect it through **Customize → Connectors** and
  enable it for the task through **+ → Connectors**. The plugin can list
  possible messages, but it cannot validate their attachments. Download a
  candidate PDF yourself and attach it to the Cowork task; the plugin validates
  it and names the Qonto transaction for manual upload. A different reviewed
  remote mail connector qualifies only when the same PDF-byte probe succeeds.
  See Anthropic's [Google Workspace connector
  limits](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors).

This release deliberately does not install or recommend a community mail
server. Use limited mode unless an independently reviewed integration passes
the same attachment test; third-party mail servers are not part of this
plugin.

**Getting started:** in Claude Code, Cowork, or Codex, first ask *"Richte den
Qonto Matchmaker ein."* In Codex, use `$qonto-matchmaker:fizard-onboard` if
the workflow is not selected automatically. For a reconciliation, ask
*"Gleiche meine Qonto-Belege für Juni 2026 ab."* In Claude Code or Cowork you
can alternatively run `/qonto-matchmaker:reconcile-invoices Juni 2026`; in Codex,
`$qonto-matchmaker:reconcile-invoices Juni 2026`. The year is optional; if
omitted, the current year is used unless that would put the month in the
future. On first use, onboarding verifies Qonto, every relevant mailbox,
attachment download, and the prerequisites for upload. The first explicitly
approved upload is the live proof of that route. If full automation is
unavailable, onboarding says so and offers a report/manual path without
claiming completion. Cowork always uses that limited path in this release.

## Feedback

Ideas and improvement suggestions are always welcome — send them to
[support@fizard.com](mailto:support@fizard.com), or hand them over in a
standard session: if your connected mailbox can send mail, the plugin composes
the message for you and sends it once you've approved the text. Dry-runs and
scheduled runs never draft or send feedback. Cowork only shows the address; it
does not draft or send mail.

## Release workflow (Fizard-internal)

1. Update skill content under `plugins/<plugin>/skills/`.
2. Bump the version (scheme `YEAR.MONTH.PATCH`) in
   `plugins/<plugin>/.codex-plugin/plugin.json` — **only there**. The Claude
   manifests deliberately carry no version: for Claude Code and Cowork every
   commit on `main` *is* a release (the commit SHA becomes the version), while
   Codex caches by manifest version and needs the bump to pick up changes.
3. Add a `CHANGELOG.md` entry under the new Codex version.
4. Run `python3 scripts/validate_repo.py` and
   `claude plugin validate .claude-plugin/marketplace.json`, then commit and
   push to `main` — CI re-runs both validations and checks required Codex fields,
   skill metadata, assets, catalogs, MCP config, and release version. Claude
   Code users with auto-update get the new state on their next start, or can
   run `/reload-plugins`. Cowork users refresh the Fizard marketplace under
   **Customize → Plugins** and start a new task. For Codex, run
   `codex plugin marketplace upgrade fizard`, then
   `codex plugin add qonto-matchmaker@fizard`, and start a new task.

## Structure

```
.claude-plugin/marketplace.json          Claude Code catalog
.agents/plugins/marketplace.json         Codex catalog
plugins/qonto-matchmaker/
├── .claude-plugin/plugin.json           Claude Code manifest (commit-SHA versioning)
├── .codex-plugin/plugin.json            Codex manifest + version
├── .mcp.json                            bundled Qonto MCP server config
└── skills/
    ├── fizard-onboard/SKILL.md          onboarding flow
    └── reconcile-invoices/SKILL.md      the monthly reconciliation
CHANGELOG.md                             what changed per release
PRIVACY.md                               plugin data flow and retention notice
.github/workflows/validate.yml           CI: manifest validation + version check
scripts/validate_repo.py                 cross-platform release checks
```

Both plugin systems expect `skills/` at the plugin root, so a single plugin
directory carries both manifests and one shared set of skills. New plugins
get their own `plugins/<name>/` directory plus an entry in **both** catalogs.
