#!/usr/bin/env python3
from __future__ import annotations

"""Render canonical scaffold docs from the manifest and Makefile help output.

[ref:common_scaffold_make_contract]
[tag:generated_scaffold_docs]
"""

import argparse
import sys
from pathlib import Path

from scaffold_tools import ROOT, common_target_names, language_names, load_manifest, run_make_help


def render_command_block(help_output: str) -> str:
    return "```text\n" + help_output.strip() + "\n```\n"


def render_root_readme(manifest: dict) -> str:
    lines = [
        "# Metaprogramming scaffolds",
        "",
        "This repository consolidates four language-specific starter scaffolds into one place and validates them with a single repeatable workflow.",
        "",
        "## Common contract",
        "",
        "Every scaffold exposes the same outer Make contract:",
        "",
    ]
    for target in manifest["commonTargets"]:
        lines.append(f"- `make {target['name']}` — {target['description']}")
    lines.extend(
        [
            "",
            "## Included scaffolds",
            "",
        ]
    )
    for language in language_names(manifest):
        metadata = manifest["languages"][language]
        lines.append(f"- [`{metadata['displayName']}`](./{metadata['path']}/README.md) — {metadata['summary']}")
    lines.extend(
        [
            "",
            "## Repository automation",
            "",
            "- `make format` regenerates canonical documentation.",
            "- `make check` validates the manifest, Makefile contracts, and deprecated-doc removal.",
            "- `make test` runs the repository test suite.",
            "- `make smoke` runs the end-to-end scaffold checks across the language folders.",
            "",
            "## Provenance",
            "",
            "The source template revision for each language is recorded in `scaffolds.json` so updates stay auditable.",
            "",
        ]
    )
    return "\n".join(lines)


def render_root_agents(manifest: dict) -> str:
    lines = [
        "# Agent playbook",
        "",
        "Use this repository as a catalog of language starter templates. Each language directory is intended to be copyable as a standalone starter while still conforming to a shared repo contract.",
        "",
        "## Shared workflow",
        "",
        "1. Run `make doctor` inside the target scaffold before changing code.",
        "2. Use `make init` to materialize local dependencies and one-time setup.",
        "3. Keep the common contract (`help`, `doctor`, `init`, `check`, `format`, `test`, `build`) intact across all scaffolds. [ref:common_scaffold_make_contract]",
        "4. Run `make format`, `make check`, and `make test` before finalizing changes in any scaffold.",
        "5. If you change a Makefile or manifest entry, regenerate docs with `make format`. [ref:generated_scaffold_docs]",
        "",
        "## Repository guardrails",
        "",
        "- Do not reintroduce the old conventions-document pattern; the canonical human+agent guidance now lives in `AGENTS.md` files.",
        "- Keep provenance in `scaffolds.json` current when syncing from external template repositories.",
        "- Preserve the per-language starter samples so smoke tests exercise a real project shape.",
        "",
        "## Language quick references",
        "",
    ]
    for language in language_names(manifest):
        metadata = manifest["languages"][language]
        lines.append(f"### {metadata['displayName']}")
        for bullet in metadata["agentHighlights"]:
            lines.append(f"- {bullet}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_language_readme(metadata: dict, help_output: str) -> str:
    lines = [
        f"# {metadata['displayName']} scaffold",
        "",
        metadata["summary"],
        "",
        "## Quickstart",
        "",
        "1. Run `make doctor` to verify the required toolchain is present.",
        "2. Run `make init` to install dependencies and perform one-time setup.",
        "3. Use `make format`, `make check`, `make test`, and `make build` as your normal development loop.",
        "",
        "## Commands",
        "",
        render_command_block(help_output).rstrip(),
        "",
        "## Starter shape",
        "",
        "Support files:",
    ]
    for rel_path in metadata["supportFiles"]:
        lines.append(f"- `{rel_path}`")
    lines.extend(["", "Starter code:"])
    for rel_path in metadata["sampleFiles"]:
        lines.append(f"- `{rel_path}`")
    lines.extend(
        [
            "",
            "## Toolchain",
            "",
            *[f"- `{tool}`" for tool in metadata["toolchain"]],
            "",
            "## Provenance",
            "",
            f"- Source template: `{metadata['sourceTemplate']['name']}`",
            f"- Imported from: `{metadata['sourceTemplate']['localPath']}`",
            f"- Source revision: `{metadata['sourceTemplate']['revision']}`",
            "",
        ]
    )
    return "\n".join(lines)


def render_language_agents(metadata: dict, common_targets: tuple[str, ...]) -> str:
    lines = [
        f"# {metadata['displayName']} scaffold agent guide",
        "",
        f"This scaffold follows the shared Make contract: {', '.join(f'`{target}`' for target in common_targets)}.",
        "",
        "## Working rules",
        "",
        "1. Start with `make doctor` and `make init`.",
        "2. Keep the starter sample code compiling and tested.",
        "3. Regenerate docs after Makefile changes with the repository root `make format`.",
        "4. Treat this directory as a copyable standalone template, not just a docs folder.",
        "",
        "## Language-specific guidance",
        "",
    ]
    for bullet in metadata["agentHighlights"]:
        lines.append(f"- {bullet}")
    lines.append("")
    return "\n".join(lines)


DOC_RENDERERS = {
    ROOT / "README.md": render_root_readme,
    ROOT / "AGENTS.md": render_root_agents,
}


def expected_documents(manifest: dict) -> dict[Path, str]:
    docs: dict[Path, str] = {}
    common_targets = common_target_names(manifest)
    for path, renderer in DOC_RENDERERS.items():
        docs[path] = renderer(manifest)
    for language in language_names(manifest):
        metadata = manifest["languages"][language]
        base = ROOT / metadata["path"]
        help_output = run_make_help(base)
        docs[base / "README.md"] = render_language_readme(metadata, help_output)
        docs[base / "AGENTS.md"] = render_language_agents(metadata, common_targets)
    return docs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest()
    docs = expected_documents(manifest)

    if args.check:
        stale: list[str] = []
        for path, content in docs.items():
            current = path.read_text() if path.exists() else None
            if current != content:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            print("Generated docs are stale:", file=sys.stderr)
            for path in stale:
                print(f"- {path}", file=sys.stderr)
            return 1
        return 0

    for path, content in docs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
