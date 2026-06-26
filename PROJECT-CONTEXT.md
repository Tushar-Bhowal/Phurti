# Phurti — Full Project Context

> **What this file is.** A complete, portable handoff document for *Phurti*. Paste it into any AI
> (Claude, ChatGPT, Gemini, a local model) in any IDE or chat, and it will understand the project
> well enough to help you modify it **without breaking the design, the constraints, or the
> multi-agent layout**. Keep it in the repo and update it whenever a decision changes.

> **How to use it with another AI.** Start your message with: *"Read this project context, then help
> me with X. Respect the constraints and the routing model — don't add features the host agent can't
> actually do, don't bloat always-loaded files, and keep one source of truth for the ruleset."* Then
> paste this whole file.

---

## 1. What the project is

**Phurti** (फुर्ती — "agility, swiftness; moving fast and light") is a portable senior-engineer
workflow for AI coding agents. One ruleset and one set of skills, installed once, working across
agents. The idea: less code, fewer tokens, less manual effort — without cutting corners on safety.

- **Repo:** `https://github.com/Tushar-Bhowal/Claude-Code-Kit` (public, MIT) — **to be renamed to
  `phurti`**; the README clone command still has a `<your-username>` placeholder to fill.
- **Status:** in testing / evolving. Sound in design and mechanically tested; not yet battle-tested
  across weeks of real use, and the multi-agent reach is uneven (see §4).
- **Audience:** full-stack developers. Claude Code is the first-class path; Codex, Copilot, and
  Antigravity are supported at lower fidelity.

---

## 2. Core philosophy (the through-line behind every decision)

1. **Context is the budget.** Agents re-read context every turn; quality drops as it fills. Most
   "efficiency" choices are really about protecting the context window.
2. **Route each concern to the mechanism built for it** (see §6). Don't cram everything into one file.
3. **Lean beats complete.** A bloated always-loaded file makes the agent ignore its own rules. For
   every line ask "would removing this cause a mistake?" If not, cut it.
4. **Ask, don't assume.** On genuine ambiguity, stop and ask — never invent a file, API, value, or
   intent. Reflect-then-confirm; never reword-and-run.
5. **Build only what's needed.** Prefer the smallest fix that fully solves the problem (the ladder,
   §10). Propose larger changes before building them.
6. **No persona costumes.** "Act as a 20-year expert" does ~nothing and can route worse. Behavior
   comes from concrete checklists, not claimed identities.
7. **Honesty over hype.** No fake metrics, no borrowed benchmark numbers, no naming other projects.
   State real wins (less re-typing, higher quality floor) and real limits. Tell users to measure.
8. **Rules are requests; hooks are guarantees.** Use the right one for the stakes — and know hooks
   only run on some hosts (§4).
9. **One source of truth.** The always-on ruleset lives in `AGENTS.md`; everything else is generated
   or appended from it (§5).

---

## 3. What's in the kit (current names)

```
phurti/
├── AGENTS.md                       # SINGLE SOURCE OF TRUTH for the always-on ruleset
├── skills/
│   ├── phurti-feature/SKILL.md     # /phurti-feature — main build/fix workflow
│   ├── phurti-fix/SKILL.md         # /phurti-fix — bug-shaped: reproduce → root cause → regression test
│   ├── phurti-audit/SKILL.md       # /phurti-audit — read-only review → one prioritized report
│   └── phurti-memory/SKILL.md      # /phurti-memory — generate/audit a lean project memory file
├── agents/
│   ├── phurti-frontend-review.md   # a11y, responsive, loading/error/empty states, design fidelity
│   ├── phurti-backend-review.md    # input validation, authz/IDOR, injection, error handling, secrets
│   ├── phurti-db-review.md         # migration safety, integrity, indexes, N+1, transactions
│   ├── phurti-test-review.md       # edge cases, real assertions, no over-mocking, regression tests
│   ├── phurti-deploy-review.md     # secrets/config, env parity, migration ordering, rollback, observability
│   └── phurti-ai-review.md         # prompt-injection safety, output validation, token/cost, privacy
├── hooks/
│   ├── block-ai-attribution.py     # PreToolUse(Bash): blocks git commits with AI/model attribution (exit 2)
│   ├── protect-tests.py            # PreToolUse(Edit): blocks removing assertions / adding skip markers
│   └── session-status.py           # SessionStart: prints git status (branch, last commit, dirty files)
├── .github/copilot-instructions.md # GENERATED adapter — GitHub Copilot rules
├── .agents/rules/phurti.md         # GENERATED adapter — Antigravity rules
├── scripts/build-adapters.sh       # regenerates the adapters from AGENTS.md; --check fails on drift
├── install.sh                      # installs per host (Claude full, Codex rules); prints copilot/antigravity steps
├── update.sh                       # same install + restart reminder
├── README.md   LICENSE (MIT)   .gitignore   PROJECT-CONTEXT.md (this file)
```

### What each command does
- **`/phurti-feature`** — build/fix anything end to end. Intake (brain-dump or `<task>`, restate +
  confirm), model recommendation, plan (waits for approval even in auto mode; plan file for big
  tasks), implement (clean comments, the ladder), verify with evidence, route to a domain review
  agent, update project memory if something durable changed, commit **only when asked** (no AI
  attribution), remind to `/clear`.
- **`/phurti-fix`** — bug-shaped: reproduce with a failing test → find the real root cause (read the
  full code path, check what recently changed, hypothesize and falsify) → smallest correct diff →
  regression test → verify. Points to `/phurti-feature` for larger work.
- **`/phurti-audit`** — read-only review of the diff/path/repo. Routes to domain agents, verifies
  each finding (`file:line`, confirmed against real behavior), explicit "do NOT flag" list, one
  prioritized report (Critical/Important/Minor). No edits, no commits.
- **`/phurti-memory`** — generate/audit/prune a lean project memory file (`AGENTS.md`, or `CLAUDE.md`
  on Claude Code). Leaves good lines alone; proposes only gaps and trims.

---

## 4. Multi-agent model (honest enforcement matrix)

| Agent | Always-on rules | Skills (`/phurti-*`) | Hooks (enforced) |
| --- | --- | --- | --- |
| **Claude Code** | `~/.claude/CLAUDE.md` (appended) | yes | yes |
| **Codex CLI** | `~/.codex/AGENTS.md` (appended) | where Agent-Skills supported | partial |
| **Copilot (VS Code)** | `.github/copilot-instructions.md` | — | — |
| **Antigravity** | `.agents/rules/phurti.md` | as skills | — |

Claude Code is fully enforced. On the instruction-only agents the rules are **advisory context only**
and the hooks do not run — an honest limit of those hosts. Do not claim otherwise in docs.

---

## 5. Single source of truth + adapters

`AGENTS.md` holds the only copy of the always-on ruleset, between the markers
`<!-- >>> phurti rules >>> -->` … `<!-- <<< phurti rules <<< -->`.

- `scripts/build-adapters.sh` regenerates `.github/copilot-instructions.md` and
  `.agents/rules/phurti.md` from that block. Run it after editing `AGENTS.md`.
- `scripts/build-adapters.sh --check` fails if an adapter drifted (wire into CI).
- `install.sh` appends the same block to `~/.claude/CLAUDE.md` (Claude) and `~/.codex/AGENTS.md`
  (Codex), idempotently (it checks for the marker).

**Rule:** never edit the adapters by hand — edit `AGENTS.md` and regenerate.

---

## 6. The routing model (where each thing belongs)

| You want to… | Put it in… | Why |
| --- | --- | --- |
| A recurring multi-step **workflow** | a **skill** | Loads on demand; near-zero tokens until used. |
| **Domain depth / review** over many files | a **subagent** | Own context; returns a summary; main context stays lean. |
| A rule that must hold **every time** | a **hook** | Deterministic — but only on Claude Code/Codex. |
| A universal preference for **every session** | `AGENTS.md` (→ appended to host memory files) | Always loaded; keep it to a few lines. |
| A **fact / reference** | verify live docs when needed | Static docs rot; the project deliberately keeps none. |

**Cost note people get backwards:** the always-loaded memory file is the *most expensive* place to
put anything (re-read every turn), not the cheapest. Skills are the cheap place. Never have a skill
auto-write into the memory file.

---

## 7. Hard constraints of host agents (don't add impossible features)

- **A skill cannot switch its own live model.** It can *recommend* a model; the user flips it. Some
  hosts have a plan→implement auto-switch alias; subagents can pin a model. No "sense difficulty and
  auto-upgrade the running model."
- **A skill cannot run `/clear` or `/compact`** — user-only. It can remind.
- **A skill cannot flip the session's permission mode.** It enforces *behavior* instead (e.g. "present
  a plan and wait, regardless of mode").
- **Rules/skills are followed reliably, not guaranteed.** Only **hooks** are deterministic — and only
  on hosts that run them.
- **Blocking hooks must use exit code 2** (exit 1 doesn't block). Hooks should **fail open** on
  unparseable input, and are skipped in untrusted workspaces.
- **Editing an agent/skill file on disk** is picked up live on Claude Code within a session for
  SKILL.md text; creating a brand-new top-level skills dir needs a restart. Other components may need
  a reload.
- **Names/aliases/tiers change** — confirm in the host's `/model` or live docs; don't hardcode trust.

---

## 8. Naming & namespacing decision (why everything is `phurti-` prefixed)

Loose skills (Phurti installs by copying `SKILL.md` into the host's skills dir) get **no automatic
namespace** — same-named skills silently override by scope. Generic verbs like `feature`/`fix`/`audit`
are the most likely to collide with a user's own skills. A plugin namespace would auto-disambiguate,
but only on Claude Code (and partly Codex) — not on the other targets, and double-prefixing under a
plugin is ugly.

Because Phurti is **multi-agent and installs as loose files**, manual prefixing is the one
disambiguation that works identically everywhere. So every command and agent carries `phurti-`:
`/phurti-feature`, `/phurti-fix`, `/phurti-audit`, `/phurti-memory`, and the six `phurti-*-review`
agents. Don't also wrap it in a plugin namespace — pick one mechanism.

---

## 9. The token lever — the ladder (in `AGENTS.md` + `/phurti-feature`)

Before writing code, stop at the first rung that holds: needn't exist → standard library → native
platform feature → already-installed dependency → one line → minimum that fully works. Never cut
input validation, error handling, security, or accessibility to shrink code.

**Honest framing:** writing less code is what actually cuts tokens, but it's **not universal** (a
reasoning model can spend more thinking tokens deliberating; review agents are real calls that add
tokens). Net effect depends on the task. The dependable wins are less code, less re-typing, and a
higher quality floor — not a guaranteed lower bill. Do not cite outside benchmark numbers.

---

## 10. Design decisions & rationale (so they aren't "fixed" by mistake)

- **Commit only when explicitly asked** — the satisfaction gate is deliberate; auto-commit was removed.
- **No static knowledge/playbook file** — it rots; principles live in the executable pieces + `AGENTS.md`.
- **Six review agents** — justified by a genuinely full-stack workflow. Delete any you never fire.
- **Plan files only for big tasks** — creating/deleting a `.md` for a one-line fix is overhead.
- **Rules in `AGENTS.md`, not auto-written per project** — coverage, not token savings; kept tiny.
- **Descriptions, not personas, on agents** — job-shaped descriptions route reliably.
- **`/phurti-feature` does NOT audit memory** — that's `/phurti-memory`'s job; keep them separate.
- **No external project names anywhere** — describe patterns generically; don't borrow others' metrics.

---

## 11. Honest limitations

- Skills/rules are reliable, not guaranteed; only hooks are deterministic, and only on Claude/Codex.
- `protect-tests` is a heuristic — can flag a legit refactor. `block-ai-attribution` reads the commit
  command string, so `git commit -F file` isn't scanned (`-m` is).
- Model recommendation is a judgment call, not a measured router.
- Token claims: not primarily a token-saver. Real wins are less code + less re-typing; review agents
  add tokens. Tell users to measure their own.
- Multi-agent reach is uneven (see §4). Adapter global paths for Copilot/Antigravity were best-effort
  and should be verified per host; project-level paths are reliable.
- Tuned to a solo full-stack workflow; other stacks/teams need trimming.

---

## 12. Install / update / maintain

**Maintain:** edit a skill/agent/hook or `AGENTS.md`, run `scripts/build-adapters.sh`, then
`git add . && git commit && git push`.

**Install (anyone):**
```
git clone https://github.com/<your-username>/phurti.git
cd phurti
bash install.sh
```
Sets up Claude Code in full, installs the ruleset for Codex at `~/.codex/AGENTS.md`, and prints copy
steps for Copilot and Antigravity. Non-destructive, safe to re-run.

**Update:** `cd phurti && git pull && bash update.sh`, then restart the agent.

---

## 13. Known open items / TODO

- [ ] **Rename the GitHub repo** `Claude-Code-Kit` → `phurti` (or push to a fresh `phurti` repo).
- [ ] **README clone command** still has `<your-username>` — replace with the real path.
- [ ] **Claim the name** — `phurti` is free on npm and has no GitHub project; grab it if publishing.
- [ ] **Smoke test as a stranger** — clone fresh on a clean machine and run `install.sh` start to finish.
- [ ] **Optional CI**: run `scripts/build-adapters.sh --check` on push so adapter drift can't reach `main`.
- [ ] LICENSE already has the real name/year (MIT).

---

## 14. Roadmap (goals, not promises — shaped by real use)

- More agents (Cursor, Windsurf, Cline, Gemini) via the same one-source → adapters pattern.
- Sharper complexity → model suggestions; optional per-stack presets.
- Battle-testing the heuristics (test-protection, audit, model recommendation) against real usage.

---

## 15. How to extend correctly (decision checklist)

1. **Does the host agent actually support it?** (§7 — no auto model-switch, no `/clear`, no permission-
   mode flip. Reframe as recommend/assist.)
2. **Where does it belong?** (§6 — workflow→skill, depth→subagent, must-happen→hook, universal→`AGENTS.md`.)
3. **Does it bloat an always-loaded file?** Cut anything inferable from code.
4. **Is it honest?** No new capability claims, no borrowed numbers, no external project names.
5. **Is it simple?** Smallest change that solves it; don't build variants "just in case."
6. **Reliable vs guaranteed?** If it must never break, it's a hook (and only enforced on Claude/Codex).
7. **One source of truth?** Ruleset changes go in `AGENTS.md`, then regenerate adapters.

When in doubt, **don't add** — restraint is what keeps this kit good. The real next step is usually to
*use it on a real task and see what rubs*, not more building.

---

## 16. Voice / tone for whoever continues this

Blunt, honest, anti-hype. Push back when an idea is wrong or impossible; explain *why*; concede when
the user has a point. Separate "good instinct" from "specific mechanism won't work." Never claim
something is 100%/perfect/bulletproof when it's an instruction (only hooks are, on some hosts). Prefer
the real trade-off over reassurance. Don't name or lean on other projects.

---

*Last updated for the Phurti rename + multi-agent layout + `phurti-` namespacing. If a host's command
name or capability has changed, trust live docs over this file and update the affected section.*
