#!/usr/bin/env python3
"""Dependency-free release checks shared by local development and CI."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "qonto-matchmaker"
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"{path.relative_to(ROOT)}: invalid JSON: {error}")
        return {}
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)}: root must be an object")
        return {}
    return value


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve_plugin_path(raw: Any, label: str) -> None:
    if not nonempty_string(raw):
        fail(f"{label}: expected a non-empty relative path")
        return
    path = (PLUGIN / raw).resolve()
    try:
        path.relative_to(PLUGIN.resolve())
    except ValueError:
        fail(f"{label}: path escapes plugin root: {raw}")
        return
    if not path.exists():
        fail(f"{label}: referenced path does not exist: {raw}")


def validate_frontmatter(skill_file: Path) -> None:
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        fail(f"{skill_file.relative_to(ROOT)}: missing YAML frontmatter")
        return
    frontmatter = text.split("\n---\n", 1)[0].splitlines()[1:]
    keys: dict[str, str] = {}
    for line in frontmatter:
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            fail(f"{skill_file.relative_to(ROOT)}: malformed frontmatter line: {line}")
            continue
        keys[key.strip()] = value.strip().strip('"\'')

    allowed = {"name", "description", "allowed-tools", "license", "metadata"}
    unknown = sorted(set(keys) - allowed)
    if unknown:
        fail(f"{skill_file.relative_to(ROOT)}: unsupported frontmatter keys: {', '.join(unknown)}")
    expected_name = skill_file.parent.name
    if keys.get("name") != expected_name:
        fail(f"{skill_file.relative_to(ROOT)}: name must equal directory '{expected_name}'")
    if not keys.get("description"):
        fail(f"{skill_file.relative_to(ROOT)}: description is required")


def validate_openai_yaml(skill_dir: Path) -> None:
    path = skill_dir / "agents" / "openai.yaml"
    if not path.is_file():
        fail(f"{path.relative_to(ROOT)}: file is required")
        return
    text = path.read_text(encoding="utf-8")
    required = (
        "display_name",
        "short_description",
        "icon_small",
        "icon_large",
        "brand_color",
        "default_prompt",
    )
    values: dict[str, str] = {}
    for key in required:
        match = re.search(rf"^  {re.escape(key)}:\s*[\"']?(.+?)[\"']?\s*$", text, re.MULTILINE)
        if not match or not match.group(1).strip():
            fail(f"{path.relative_to(ROOT)}: interface.{key} is required")
            continue
        values[key] = match.group(1).strip().strip('"\'')

    prompt = values.get("default_prompt", "")
    if f"${skill_dir.name}" not in prompt:
        fail(f"{path.relative_to(ROOT)}: default_prompt must mention ${skill_dir.name}")
    for key in ("icon_small", "icon_large"):
        raw = values.get(key)
        if raw:
            asset = (skill_dir / raw).resolve()
            try:
                asset.relative_to(skill_dir.resolve())
            except ValueError:
                fail(f"{path.relative_to(ROOT)}: {key} escapes the skill directory")
                continue
            if not asset.is_file():
                fail(f"{path.relative_to(ROOT)}: missing {key} asset {raw}")


def validate_agent_instructions() -> None:
    agents = ROOT / "AGENTS.md"
    claude = ROOT / "CLAUDE.md"
    if not agents.is_file():
        fail("AGENTS.md is required")
    if not claude.is_file():
        fail("CLAUDE.md is required")
        return
    if claude.read_text(encoding="utf-8").strip() != "@AGENTS.md":
        fail("CLAUDE.md must contain only @AGENTS.md")


def validate() -> None:
    validate_agent_instructions()
    claude_catalog = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    codex_catalog = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    claude_manifest = load_json(PLUGIN / ".claude-plugin" / "plugin.json")
    codex_manifest = load_json(PLUGIN / ".codex-plugin" / "plugin.json")
    mcp = load_json(PLUGIN / ".mcp.json")

    expected = "qonto-matchmaker"
    canonical_description = (
        "Finds missing Qonto receipts. When the mail connector returns PDF "
        "files, Claude Code and Codex validate matches and upload them after "
        "user approval. Cowork validates attached PDFs for manual upload."
    )
    for label, manifest in (("Claude manifest", claude_manifest), ("Codex manifest", codex_manifest)):
        if manifest.get("name") != expected:
            fail(f"{label}: name must be {expected}")

    version = codex_manifest.get("version")
    if not nonempty_string(version) or not re.fullmatch(r"\d{4}\.\d+\.\d+", version):
        fail("Codex manifest: version must match YEAR.MONTH.PATCH")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    heading = re.search(r"^## (\d{4}\.\d+\.\d+)\b", changelog, re.MULTILINE)
    if not heading or heading.group(1) != version:
        fail("Codex manifest version must match the first CHANGELOG release")

    interface = codex_manifest.get("interface")
    if not isinstance(interface, dict):
        fail("Codex manifest: interface must be an object")
        interface = {}
    for key in (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "brandColor",
    ):
        if not nonempty_string(interface.get(key)):
            fail(f"Codex manifest: interface.{key} must be a non-empty string")
    if len(interface.get("shortDescription", "")) > 30:
        fail("Codex manifest: interface.shortDescription must be at most 30 characters")
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities or not all(
        nonempty_string(item) for item in capabilities
    ):
        fail("Codex manifest: interface.capabilities must contain non-empty strings")
    for key in ("composerIcon", "logo"):
        resolve_plugin_path(interface.get(key), f"Codex manifest interface.{key}")
    resolve_plugin_path(codex_manifest.get("skills"), "Codex manifest skills")
    resolve_plugin_path(codex_manifest.get("mcpServers"), "Codex manifest mcpServers")

    for key in ("homepage", "repository"):
        value = codex_manifest.get(key)
        if not nonempty_string(value) or not value.startswith("https://"):
            fail(f"Codex manifest: {key} must be an https URL")
    for key in ("websiteURL", "privacyPolicyURL"):
        value = interface.get(key)
        if not nonempty_string(value) or not value.startswith("https://"):
            fail(f"Codex manifest: interface.{key} must be an https URL")
    terms_url = interface.get("termsOfServiceURL")
    if terms_url is not None and (
        not nonempty_string(terms_url) or not terms_url.startswith("https://")
    ):
        fail("Codex manifest: interface.termsOfServiceURL must be an https URL when present")
    if not (ROOT / "PRIVACY.md").is_file():
        fail("PRIVACY.md is required for the plugin-specific privacyPolicyURL")

    claude_plugins = claude_catalog.get("plugins")
    if not isinstance(claude_plugins, list) or not any(
        isinstance(item, dict) and item.get("name") == expected and item.get("source") == "./plugins/qonto-matchmaker"
        for item in claude_plugins
    ):
        fail("Claude marketplace: qonto-matchmaker source is missing or wrong")
    codex_plugins = codex_catalog.get("plugins")
    if not isinstance(codex_plugins, list) or not any(
        isinstance(item, dict)
        and item.get("name") == expected
        and item.get("source", {}).get("path") == "./plugins/qonto-matchmaker"
        for item in codex_plugins
    ):
        fail("Codex marketplace: qonto-matchmaker source is missing or wrong")

    descriptions = [
        claude_manifest.get("description"),
        codex_manifest.get("description"),
        interface.get("longDescription"),
    ]
    if isinstance(claude_plugins, list):
        descriptions.extend(
            item.get("description")
            for item in claude_plugins
            if isinstance(item, dict) and item.get("name") == expected
        )
    if isinstance(codex_plugins, list):
        descriptions.extend(
            item.get("description")
            for item in codex_plugins
            if isinstance(item, dict) and item.get("name") == expected
        )
    if any(description != canonical_description for description in descriptions):
        fail("Marketplace and manifest descriptions must use the capability-qualified copy")

    qonto = mcp.get("mcpServers", {}).get("qonto", {})
    if qonto != {"type": "http", "url": "https://mcp.qonto.com/mcp"}:
        fail(".mcp.json: qonto must use the official HTTPS endpoint")

    skill_dirs = sorted(path.parent for path in (PLUGIN / "skills").glob("*/SKILL.md"))
    if not skill_dirs:
        fail("Plugin must contain at least one skill")
    for skill_dir in skill_dirs:
        validate_frontmatter(skill_dir / "SKILL.md")
        validate_openai_yaml(skill_dir)


if __name__ == "__main__":
    validate()
    if ERRORS:
        print("Release validation failed:", file=sys.stderr)
        for error in ERRORS:
            print(f"- {error}", file=sys.stderr)
        sys.exit(1)
    print("Release validation passed")
