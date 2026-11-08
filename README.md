# Phurti

A portable senior-engineer workflow for Claude Code and Codex. Plan, implement, verify, review, and resume work with the same five skills. *Phurti* (फुर्ती) means agility: build only what the task needs, with evidence that it works.

## What is included

| Skill | Purpose |
| --- | --- |
| `phurti-architect` | Explore requirements and alternatives, then produce an approved architecture and phased implementation plan. |
| `phurti-feature` | Build a feature or refactor: recommend a model, plan, implement, verify, and obtain a focused review. |
| `phurti-fix` | Reproduce a bug, diagnose its root cause, make the smallest correct fix, and prove it with a regression check. |
| `phurti-audit` | Review a diff, path, or repository and save actionable findings. No source edits or commits. |
| `phurti-memory` | Inspect or refine project instructions while preserving accurate existing content. Explicit invocation only. |

Six domain reviewers cover frontend, backend, database, tests, deployment, and AI integrations. Four hooks check commit attribution and test weakening, show session status, and preserve a handoff through compaction. Skills recommend a model before substantial work and commit only when explicitly asked.

## Compatibility

| Host | Rules | Skills | Reviewers | Hooks |
| --- | --- | --- | --- | --- |
| Claude Code | `~/.claude/CLAUDE.md` | `/phurti-*` | Native Markdown agents | Claude tool and lifecycle inputs |
| Current local Codex CLI / IDE | `$CODEX_HOME/AGENTS.md` | `$phurti-*` | Native TOML agents | Codex tool and lifecycle inputs; trust required |
| Codex desktop local mode | Same local configuration | Select a skill | Uses local Codex agents | Review hooks in the app; verify your client |
| Copilot / Antigravity | Generated rule adapters | Not installed | Not installed | Not installed |

Codex home defaults to `~/.codex`; skills go in `~/.agents/skills`. Native custom agents and lifecycle hooks require a current Codex client. This implementation targets the documented formats and was checked with Codex CLI `0.164.0-alpha.11.1`; older versions may differ. Cloud orchestration has different hook support and is not covered by this local installer.

See the official [skills](https://learn.chatgpt.com/docs/build-skills), [subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), and [hooks](https://learn.chatgpt.com/docs/hooks) documentation. A successful file installation does not prove that a particular client has enabled or trusted the hooks.

## Install

Requirements: Python 3.9+, git, and the host you intend to use. Development tests use Python 3.11+ for the standard-library TOML parser. No third-party Python packages are required by the kit.

```sh
git clone https://github.com/Tushar-Bhowal/Phurti.git phurti
cd phurti
bash install.sh                  # both Claude Code and Codex
bash install.sh --agent codex    # Codex only
bash install.sh --agent claude   # Claude Code only
```

The installer preserves unrelated settings, hooks, and instructions. It replaces the marked Phurti rule block on updates and refreshes Phurti skill, reviewer, and hook files. Changed files get a sibling `.phurti-backup` containing their previous version. Invalid JSON or malformed rule markers stop installation before writing configuration; disk errors during writing can still leave a partial install, which can be rerun.

`CODEX_HOME`, when set, controls the Codex rules, agents, and hooks destination. It does not move user skills from `~/.agents/skills`. `--home /tmp/phurti-check` stages an installation under that directory, ignoring `CODEX_HOME` and leaving your actual user configuration alone.

Codex hooks are merged into `hooks.json`; `config.toml`, model choices, permission settings, and existing inline hooks are preserved. If you previously configured Phurti hooks manually in TOML or another active layer, remove those duplicates yourself: Codex runs hooks from all active sources.

## Activate and check

After installation, reload your client if the skills have not appeared.

For Codex CLI:

1. Open `/skills` and check for all five `phurti-*` skills.
2. Open `/hooks`, review the four Phurti hooks, and trust them. New or changed hook definitions may require another review. Hooks disabled by user or managed policy remain disabled.
3. Invoke `$phurti-feature` with a small task and confirm it recommends a model and follows the workflow.
4. During a domain review, inspect `/subagents` to confirm the selected reviewer ran. If delegation is disabled or unavailable, the skill reports a non-independent fallback review.

In the IDE, use the skill selector or `$` mention and the model picker. If hook review is not exposed in that client, review the same local hooks through Codex CLI. In the desktop app, use the skill selector and Settings > Hooks. GUI activation and account-specific model availability should be checked in the client you use.

For Claude Code, check `/phurti-feature`, `/agents`, and `/hooks` after reloading.

## Use

Codex CLI / IDE examples:

```text
$phurti-architect design a multi-tenant billing system
$phurti-feature build the architecture in .phurti/plans/architecture-billing.md
$phurti-feature add a logout button that clears the session
$phurti-fix login fails after the session expires
$phurti-audit diff
$phurti-audit src/auth
$phurti-memory refine this project's instructions
```

On Claude Code, replace `$phurti-` with `/phurti-`. A bare feature invocation asks for the task; audit defaults to the current diff. The feature workflow respects plans already approved in the conversation. Reviewers are selected by the actual domain; all six do not run by default.

## Model recommendations

Phurti suggests a model, reasoning effort, and a brief reason. It continues on the model you select and does not change your session or write model defaults into configuration.

| Work | Claude Code | Codex starting recommendation |
| --- | --- | --- |
| Clear small edits / straightforward fixes | Haiku | GPT-6 Luna |
| Features / localized debugging / focused review | Sonnet | GPT-6.1 Sol |
| Difficult architecture / cross-system diagnosis | Opus | GPT-6 Astra |
| Writing / visual understanding / computer use | Choose for the task | Consider GPT-6.1 Terra where available |

These are workload recommendations, not claims of equivalent model capability. The Codex policy was checked against [official model guidance](https://learn.chatgpt.com/docs/models) on 2026-11-08. Availability varies by client, account, and workspace. The skills use known available models and check current guidance when uncertain. Start with the supported default effort (Luna High, Astra Light/`low`, Sol's client default), then increase it for harder work. Codex CLI uses `/model`; IDE and desktop clients expose a model picker.

Claude reviewers retain their existing `model: sonnet`. Generated Codex reviewers inherit the parent/default subagent model and effort, so installation does not pin a model unavailable to your account. Codex can honor an explicit supported subagent model choice; inheritance does not guarantee a cheaper review.

## Plans and continuity

New scratch state lives at the repository root:

```text
.phurti/
├── plans/                    # architecture, audit findings, implementation plans
└── handoff.md                # current goal, done, next steps, decisions, verification
```

The skills add `.phurti/` to the project's ignore file when writing scratch state. They overwrite a short handoff at useful phase boundaries and completion. SessionStart loads it on startup/resume and after compaction when the host delivers that event. Launching inside a subdirectory still finds the repository root.

Existing `.claude/plans/` files are read in place when supplied. Session recovery prefers `.phurti/handoff.md` and falls back to `.claude/handoff.md`; installation does not move or delete old files. The compaction hook preserves an existing handoff, or creates git breadcrumbs if none exists after adding a local Git exclusion for `.phurti/` when needed. It cannot make the model write a narrative summary at the last instant. Without active hooks, skills read the handoff explicitly on resume.

## Hook coverage and permissions

- Commit attribution checks inspect shell commands containing `git commit`, including readable `-F`/`--file` message files. They reject common attribution signatures and co-author trailers. They do not intercept every way to create a commit: aliases, dynamically constructed messages, shell working-directory changes, and later interactive input can evade the heuristic.
- Test protection checks Claude `Edit`/`MultiEdit`/`Write` inputs and Codex `apply_patch` changes for reduced assertion counts, added skip markers, and Codex test deletion/moves out of recognized test paths. It can flag legitimate refactors and miss semantic weakening or edits made through arbitrary shell scripts. It is not a proof of test quality.
- Hooks return exit code 2 to deny recognized violations. Invalid input and unsupported tool paths are not a universal enforcement boundary. A configuration file alone does not mean a hook is running.
- Claude installs native `.env` access prompts. These are not ported as fictional Codex `permissions.ask` rules. Codex keeps its existing sandbox and approval policy; Phurti does not add a blanket `.env` read prompt or claim that a workspace-readable secret is inaccessible. Keep real credentials outside agent-readable workspaces and use your platform's native controls.
- Review agents are instructed not to edit. Codex agents inherit parent permissions; a custom agent file does not create a separate read-only sandbox.

For commit-time secret detection across agents, use an existing scanner such as gitleaks or trufflehog. Phurti does not install one or replace your Git hooks.

## Update and maintain

```sh
git pull
bash update.sh --agent codex       # omit --agent to update both
bash scripts/build-adapters.sh     # regenerate after rules/reviewer edits
bash scripts/build-adapters.sh --check
python3 -m unittest discover -s tests -v
```

`AGENTS.md` is the rule source. `agents/*.md` is the reviewer source; the generator produces Codex TOML agents under `adapters/codex/agents/` along with the existing Copilot/Antigravity rules. Do not edit generated adapters manually. Skills are shared source files, copied with their resources to each host.

Tests cover staged fresh/repeated installation, preservation and failure handling, native-format payloads for both hosts, generated TOML, and handoff recovery. A native Codex app-server check also parsed all five staged skills without errors and recognized the four hook definitions through temporary session configuration; they remained untrusted. The temporary project itself was untrusted, so this did not verify loading project hook files or running trusted hooks. These checks do not establish GUI or cloud compatibility. Test in your actual client using the activation steps above.

For Copilot, copy `.github/copilot-instructions.md` into your project. For Antigravity, copy `.agents/rules/phurti.md`. Those adapters provide advisory rules only.

## License

MIT — see [LICENSE](LICENSE).
