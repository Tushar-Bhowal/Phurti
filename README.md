# Phurti

A portable senior-engineer workflow for AI coding agents. One ruleset, one set of skills — installed once, working across agents. *Phurti* (फुर्ती): agility, swiftness — moving fast and light. That's the whole idea — less code, fewer tokens, less manual effort, without cutting corners on safety.

> In testing and evolving. Built against current agent formats (mid-2026); these shift, so if a path or command changes, the principles still hold — update the file and send a PR.

## The problem it solves

Working with an AI coding agent, the same friction shows up every day, on every tool:

- You **re-type the same instructions** each task — plan first, write tests, verify, no AI in the commit message.
- Output is **inconsistent**, the agent **over-engineers** simple work, **over-comments** (a banner on every file), or **commits before you're ready**.
- Commits get **AI-attribution footers** you don't want; tests quietly get **weakened** to pass.
- Different agents (Claude Code, Codex, Copilot, Antigravity) each need the same rules in **their own format**.

Phurti fixes each with the right mechanism — a workflow skill for the repetition, read-only review agents for depth, deterministic hooks for the rules that must never break, and one portable ruleset for every agent.

| Friction | Handled by |
| --- | --- |
| Re-typing the workflow every time | `/phurti-feature` skill |
| Bug fixes that patch the symptom | `/phurti-fix` (reproduce → root cause → regression test) |
| Wanting a review without changes | `/phurti-audit` (read-only, one prioritized report) |
| Over-engineering / wasted tokens | the **build-only-what's-needed ladder** (in the ruleset + skills) |
| Banner/narration & noisy comments | the ruleset (essentials only) |
| AI footers in commits | commit-block hook (enforced, Claude Code/Codex) |
| Weakened / skipped tests | test-protect hook (enforced, Claude Code/Codex) |
| Same rules across many agents | one `AGENTS.md` + generated per-agent adapters |

## Works with

| Agent | Always-on rules | Skills (`/phurti-feature` etc.) | Hooks (enforced) |
| --- | --- | --- | --- |
| **Claude Code** | ✅ `~/.claude/CLAUDE.md` | ✅ | ✅ |
| **Codex CLI** | ✅ `AGENTS.md` | ✅ where Agent-Skills supported | ⚠️ partial |
| **Copilot (VS Code)** | ✅ `.github/copilot-instructions.md` | — | — |
| **Antigravity** | ✅ `.agents/rules/` | as skills | — |

Claude Code is the first-class, fully-enforced path. On the instruction-only agents the rules are **advisory** (loaded as context), and the hooks don't apply — that's an honest limit of those hosts, not a bug.

## What's inside

| Piece | What it does |
| --- | --- |
| `/phurti-architect` | Design a whole app or a feature **before any code** (Opus-work). Draws out requirements/constraints, maps the existing code, weighs 2–3 approaches, picks one with the trade-offs stated, then phases it into a build plan — written to an architecture doc that `/phurti-feature` implements. Skill-shaped orchestrator; writes no code. |
| `/phurti-feature` | Build/phurti-fix anything end to end. Brain-dump or `/phurti-feature <task>`; it restates + confirms, recommends a model, plans, implements (clean comments, build-only-what's-needed), verifies with evidence, routes to a review agent, and commits **only when you ask** — no AI attribution. |
| `/phurti-fix` | Bug-shaped: reproduce with a failing test → find the **root cause** (not the symptom) → smallest correct diff → regression test → verify. Points to `/phurti-feature` for larger changes. |
| `/phurti-audit` | **Read-only** review of the diff, a path, or the repo. Routes to domain agents, verifies each finding (`file:line`), returns one prioritized report. No edits, no commits. |
| `/phurti-memory` | Generate / audit / prune a lean project memory file (`AGENTS.md`, or `CLAUDE.md` on Claude Code). Leaves good lines alone; proposes only gaps and trims. |
| 6 review agents | Read-only domain reviewers — frontend, backend, db, test, deploy, ai — auto-invoked by domain, each returning a prioritized list. |
| 3 hooks | Block AI-attributed commits, block test weakening, print git status into every session. The first two are enforced every time (Claude Code/Codex). |
| `AGENTS.md` | The single source of truth for the always-on ruleset. Per-agent adapters are generated from it. |

## Token reduction — honest version

The reliable lever is **writing less code**, via the ladder in `AGENTS.md`: before writing, stop at the first rung that holds — needn't exist → stdlib → native feature → installed dep → one line → minimum that works; never cutting validation, error handling, security, or accessibility. Writing less code is what actually cuts tokens — but it's **not universal**: a reasoning model that spends thinking tokens deliberating the rungs can go the other way, and the review agents are real calls that add tokens. Net effect depends on the task. Measure your own. The dependable wins are **less code, less re-typing, and a higher quality floor** — not a guaranteed lower bill.

## Requirements

- The agent you're using (Claude Code, Codex, Copilot, or Antigravity)
- **Python 3** for the hooks (Claude Code/Codex) — `python3 --version`
- **git**

## Install

```
git clone https://github.com/Tushar-Bhowal/Phurti.git phurti
cd phurti
bash install.sh
```

`install.sh` sets up the Claude Code kit in full, installs the ruleset for Codex at `~/.codex/AGENTS.md`, and prints copy steps for Copilot and Antigravity. Non-destructive and safe to re-run. (Or from the zip: unzip, `cd` in, `bash install.sh`.)

## Update

```
cd phurti && git pull && bash update.sh
```

Then restart your agent so it reloads skills, agents, and rules.

## Use

```
/phurti-architect a multi-tenant billing system         # design an app/feature before any code
/phurti-feature build the architecture in .claude/plans/architecture-billing.md
/phurti-feature                                    # bare: brain-dump, it restates & confirms
/phurti-feature add a logout button that clears the session
/phurti-fix login fails after the session times out
/phurti-audit                                      # read-only review of the current diff
/phurti-audit src/auth                             # audit a specific area
/phurti-memory                               # generate/phurti-audit this project's memory file
```

Attach an image or paste an error log alongside `/phurti-feature` when relevant. Review agents auto-route by domain; don't run all six on every task. For big multi-session work the skill keeps a worklog in `.claude/plans/` (add to `.gitignore`).

## Where everything lands

```
~/.claude/                       # Claude Code
├── settings.json                # hooks merged in
├── CLAUDE.md                    # rules appended (your content preserved)
├── skills/{phurti-architect,phurti-feature,phurti-fix,phurti-audit,phurti-memory}/SKILL.md
├── agents/phurti-{frontend,backend,db,test,deploy,ai}-review.md
└── hooks/{block-ai-attribution,protect-tests,session-status}.py

~/.codex/AGENTS.md               # Codex: rules appended
<your repo>/.github/copilot-instructions.md   # Copilot (copy in)
<your repo>/.agents/rules/phurti.md            # Antigravity (copy in)
```

## How it stays in sync

`AGENTS.md` is the one source of truth for the ruleset. The per-agent adapter files are generated from it:

```
bash scripts/build-adapters.sh          # regenerate adapters after editing AGENTS.md
bash scripts/build-adapters.sh --check  # CI: fail if an adapter has drifted
```

## Roadmap (goals, not promises — shaped by real use)

- More agents (Cursor, Windsurf, Cline, Gemini) via the same one-source → adapters pattern.
- Sharper complexity → model suggestions and optional per-stack presets.
- Battle-testing the heuristics (test-protection, audit, model recommendation) against real usage.

If a goal matters to you, open an issue or PR.

## Notes & honest limits

- **Rules vs hooks:** skills and rules are *followed* reliably; hooks *enforce* the two non-negotiable ones every time — but hooks only run on Claude Code/Codex. Elsewhere those rules are advisory.
- **Skills are largely portable** (the Agent Skills spec is cross-tool), but each host's exact paths differ; the install notes cover the ones built here.
- **Heuristics aren't perfect:** the test-protect hook can occasionally flag a legit refactor; the model recommendation is a judgment call. Tune to your stack as you use it.
- **Secrets:** install adds native `permissions.ask` rules so the agent must **ask before reading a `.env`** (even in auto-accept mode), and the ruleset forbids hardcoding secrets or committing `.env` values. These are defense-in-depth, not a wall — keep real keys out of the machine the agent sees (dummy values locally; real secrets only in your deploy environment). For commit-time protection, add a real secret-scanner (e.g. **gitleaks** or **trufflehog**) as a git pre-commit hook — the kit recommends it but doesn't install it, and a git-level scanner protects you across every agent, not just Claude Code.

## License

MIT — see [LICENSE](LICENSE).
