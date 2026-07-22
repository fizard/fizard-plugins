# Fizard Plugins

Plugins and agent skills by [Fizard](https://fizard.com). Qonto Matchmaker runs
in local Claude Code sessions in the desktop app and CLI, Claude Cowork, and
the Codex app and CLI.

## Install

### Claude Code — desktop app and CLI

The Fizard marketplace is not listed automatically. No repository checkout is
needed.

#### Desktop app (no CLI required)

**Prerequisites:** a Pro, Max, Team, or Enterprise plan. On Windows, install
Git before starting a local Code-tab session.

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

See Anthropic's [desktop quickstart](https://code.claude.com/docs/en/desktop-quickstart)
and [plugin installation guide](https://code.claude.com/docs/en/discover-plugins).

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

**Prerequisites:** a paid Claude plan. On Team and Enterprise plans, an owner
must enable Cowork and Skills.

1. Open **Cowork → Customize → Plugins**.
2. Under **Personal plugins**, select **+ → Add marketplace → Add from a
   repository**.
3. Enter `https://github.com/fizard/fizard-plugins`.
4. Open **Fizard**, select **Qonto Matchmaker by Fizard**, and choose
   **Install**.
5. Start a new Cowork task and choose **Manually approve**.

Personal plugins are installed on the current computer. See Anthropic's
[plugin guide for Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).

Cowork reads Qonto, creates a missing-receipt report, and validates PDFs you
attach. You then attach the validated file to the named transaction in Qonto.
See Anthropic's [Cowork safety
guidance](https://support.claude.com/en/articles/13364135-use-claude-cowork-safely).

For a manual update, open **Cowork → Customize → Plugins**. Under **Personal
plugins**, open **Fizard** and then Qonto Matchmaker. Use **Update** or
**Reinstall** when shown, then start a new Cowork task.

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

Qonto Matchmaker finds Qonto transactions with missing receipts. When the mail
connector returns PDF files, Claude Code and Codex validate invoice matches
with six checks and upload them after the user approves the mapping. Cowork
finds missing receipts and validates attached PDFs for manual upload. The final
report shows changes, open items, known owners, and unresolved checks.

*Qonto Matchmaker is an independent Fizard product — not affiliated with
or endorsed by Qonto.*

**Data and permissions:** the plugin contains instructions and Qonto connector
configuration. It has no Fizard backend for matching and sends no invoice,
mailbox, or bank data to Fizard. The selected AI surface, mail provider, and
Qonto process the data. Claude Code and Codex upload only after the user
approves the final mapping. In Cowork, the user uploads each validated file.
See the [data and privacy notice](PRIVACY.md). Send privacy questions to
[privacy@fizard.com](mailto:privacy@fizard.com).

Before an approved upload, the plugin may read PDFs on competing Qonto
transactions. It compares the fields and hash needed to prevent duplicate use;
it does not audit their accounting correctness.

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
- **Claude Code:** connect a mail MCP that you or your organization has
  reviewed and that returns PDF files. [Google's official Gmail
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

Use a mail connector that you or your organization has reviewed. Full matching
starts only after it passes the same attachment test. Until then, use the
report or manual-file path.

**Getting started:** in Claude Code, Cowork, or Codex, first ask *"Richte den
Qonto Matchmaker ein."* In Codex, use `$qonto-matchmaker:fizard-onboard` if
the workflow is not selected automatically. For a reconciliation, ask
*"Gleiche meine Qonto-Belege für Juni 2026 ab."* In Claude Code or Cowork you
can alternatively run `/qonto-matchmaker:reconcile-invoices Juni 2026`; in Codex,
`$qonto-matchmaker:reconcile-invoices Juni 2026`. The year is optional. If it
would place the month in the future, the plugin asks. On first use, onboarding
checks Qonto, every relevant mailbox, PDF download, and upload prerequisites.
The first approved upload proves that route. Cowork reports missing receipts
and validates attached PDFs for manual upload.

## Feedback

Send questions and feedback to
[support@fizard.com](mailto:support@fizard.com). In an interactive Claude Code
or Codex session with a mail sender, the plugin can draft the message and send
it only after the user approves the text. Cowork shows the address.

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
AGENTS.md                               shared agent instructions
CLAUDE.md                               Claude Code import of AGENTS.md
.claude-plugin/marketplace.json         Claude Code catalog
.agents/plugins/marketplace.json        Codex catalog
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
