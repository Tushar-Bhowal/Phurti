# Phurti project context

Phurti is a portable rules and workflow kit for Claude Code and local Codex. Read [README.md](README.md) for installation, commands, model policy, coverage, and activation instructions. Read [AGENTS.md](AGENTS.md) for the always-on rules.

## Sources and adapters

- `AGENTS.md` contains the canonical marked rules block. Install/update replaces only that block in host instructions and preserves personal content around it.
- `skills/phurti-*/SKILL.md` contains five shared workflows: architect, feature, fix, audit, memory. Each reads the user's invoking message, follows host conventions, recommends an available model, and respects prior approval.
- `agents/*.md` contains the six canonical domain reviewers, including Claude frontmatter. Generate Codex `name`, `description`, and `developer_instructions` TOML with `bash scripts/build-adapters.sh`.
- `adapters/codex/agents/*.toml`, `.github/copilot-instructions.md`, and `.agents/rules/phurti.md` are generated. Never edit them directly. Check drift with `bash scripts/build-adapters.sh --check`.
- `skills/phurti-memory/agents/openai.yaml` preserves explicit-only invocation on Codex, corresponding to its Claude `disable-model-invocation` field. Other skills remain available for implicit selection.

## Installation

`install.sh` and `update.sh` call the standard-library Python installer in `scripts/install.py`. Python 3.9+ is sufficient for installation and hooks. Use Python 3.11+ for development tests (`tomllib`). No package installation is required.

- Default: install both agents. `--agent claude` and `--agent codex` select one host.
- Claude: `~/.claude/{CLAUDE.md,settings.json,skills,agents,hooks}`.
- Codex: `${CODEX_HOME:-~/.codex}/{AGENTS.md,hooks.json,agents,hooks}`; skills always use `~/.agents/skills`.
- `--home PATH` stages both layouts under PATH and ignores `CODEX_HOME`, without changing environment variables or the real user's settings.
- Read and validate the selected hosts' existing rule blocks and JSON before writing. Never replace malformed configuration with an empty object.
- Preserve unrelated hooks and settings. Refresh owned handlers, avoid duplication on rerun, and back up changed files to sibling `.phurti-backup` files. Writes are atomic per file, not transactional across the installation.
- Codex `config.toml` is untouched. Manually duplicated inline Phurti hooks must be reconciled by the user because all active hook layers run.

## Host differences

Use `/phurti-*` on Claude Code and `$phurti-*` or the skill selector on Codex. Avoid assuming Claude-only argument substitution, tools, memory, or commands exist on Codex. A missing question tool means ask in chat. A missing reviewer means disclose a non-independent review pass; never claim delegation happened.

Model names are recommendations, checked against host availability and current official guidance when uncertain. Skills do not switch the root session. Claude reviewer files retain Sonnet; generated Codex reviewers inherit the parent/default subagent model and effort. Custom agent instructions do not create a separate read-only sandbox.

The local Codex implementation targets the current official skill, custom-agent, and hook formats, with CLI `0.164.0-alpha.11.1` used during development. Do not infer compatibility with older releases or cloud orchestration. Verify GUI behavior in the actual client before making a stronger claim.

## Hooks and continuity

- `block-ai-attribution.py`: heuristic command/message-file inspection of `git commit`. Exit 2 blocks a matched attribution signature. Arbitrary shell evaluation and all commit entry points are not covered.
- `protect-tests.py`: Claude Edit/MultiEdit/Write and Codex apply_patch. Compare assertions and skip markers per affected test. Detect Codex test deletion and moves outside recognized test paths. Shell-based file writes and semantic weakening remain outside its coverage.
- `session-status.py`: inject bounded git status and a handoff from the git root using the event's cwd. Shared handoff wins; legacy Claude handoff is fallback.
- `pre-compact.py`: preserve the handoff; create git-only breadcrumbs if none exists. On Codex emit JSON because plain text is ignored for this event. It cannot request a guaranteed model turn before compaction.
- `session_context.py`: common event input, git-root, status, and handoff lookup helpers. It is a helper, not a fifth registered hook.

New plans and handoffs use `.phurti/plans/` and `.phurti/handoff.md`. Ignore `.phurti/` in task repositories. Read supplied legacy `.claude/plans/` files in place. Refresh a narrative handoff during feature/fix phase boundaries and completion; overwrite it and keep it under about 40 lines. A handoff is scratch task state, not a growing memory log.

Codex hooks need the user's trust and may be disabled by local or managed configuration. Installation never bypasses trust or changes sandbox/approval policy. Claude `.env` ask rules do not have a direct Codex settings.json equivalent; do not claim equivalent secret-file read prompts. Rules and heuristics are useful guardrails, not an unbreakable enforcement boundary.

## Verification

```sh
python3 -m unittest discover -s tests -v
bash scripts/build-adapters.sh --check
bash -n install.sh update.sh scripts/build-adapters.sh
git diff --check
```

Tests use temporary directories and native-format payloads without modifying the real user's configuration. Include behavior for both hosts when changing hooks. Exercise install/update preservation, malformed settings, paths containing spaces/quotes, and idempotence when changing installation.

The feature workflow requires independent review when available. Audit runs only checks compatible with its read-only scope and exits early on an empty diff. Commits and pushes require an explicit user instruction.
