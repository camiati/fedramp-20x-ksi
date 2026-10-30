# CLAUDE.md

Context for Claude Code when working in this repository.

## What this repo is

A public portfolio and personal reference project: the FedRAMP 20x Key Security Indicators as code. It is **theoretical**. There is no real system, AWS account, or Vanta tenant behind it, and none will be connected.

## Hard rules

- **No work material.** Never copy employer data, code, configuration, names, account IDs, or tenant details into this repo, including from other folders or repos on this machine.
- **Never use this machine's cloud or SaaS credentials.** No `aws` CLI commands, no reads of `~/.aws/`, no calls to a real Vanta tenant. These are also blocked in `.claude/settings.json`.
- **Integrations are built against fixtures.** API clients are tested with recorded responses and local mock servers only.
- **Never commit to `main`.** All changes go through a branch and pull request.
- **Never put secrets in any file.**

## Conventions

- **Upstream data is pinned and unchanged.** Files in `data/` are byte-for-byte copies from FedRAMP/rules at the commit in `data/upstream.json`. To update: copy the new files, update the commit and SHA-256 values, then update the expectations in `tests/test_catalog.py` in the same pull request.
- **Follow FedRAMP's AGENTS.md** when reading the rules: validate against the schema, use class-specific statements as given, and never invent a missing class variant or a normative force for a KSI.
- **Measures target Class C.** Every theme in `measures/` needs at least 2 automated measures per KSI (FRC-CSX-VVK), and tests enforce it. Measures describe the theoretical AWS + Terraform + GitHub service, never a real one. Field reference: `measures/README.md`. Update the readiness table in the README when measures change.
- **Cite IDs.** Refer to indicators by ID (`KSI-CED-RAT`) and controls as FedRAMP writes them (`at-2.2`).
- **Actions are pinned to full commit SHAs** with the version in a comment: `uses: actions/checkout@<sha> # v7.0.1`.
- **Python with uv.** Run `uv run ruff check`, `uv run ruff format --check`, and `uv run pytest` before committing.
- **README stays current:** new files get a row in "What's here"; Known gaps and Roadmap are updated with each change.

## Workflow

1. Create a branch.
2. Make the change.
3. Run lint, format, and tests locally.
4. Update the README.
5. Commit with a descriptive message, push, and open a pull request.

## Working with the owner

- Go **one step at a time**, and explain what a change does before making it.
- Ask before committing or pushing.
- Be direct and concise. Confirm facts rather than guessing; say so when unsure.
