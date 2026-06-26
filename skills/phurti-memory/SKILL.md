---
name: phurti-memory
description: Generate, audit, or refine the best possible project memory file (AGENTS.md, or CLAUDE.md on Claude Code) for THIS repo — lean, high-signal, grounded in the actual code. On an existing file it leaves good content untouched and proposes only genuine gaps and trims.
argument-hint: [optional note, e.g. "monorepo" or "just refine existing"]
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Build the best project memory file for this repo

The project memory file is the always-on context an agent reads every session. Use `AGENTS.md` (the cross-tool standard most agents read) by default; on Claude Code use `CLAUDE.md`. If both exist, treat `AGENTS.md` as canonical and keep them consistent.

Goal: a memory file that materially changes your decisions in this repo, and nothing more. Write it the way you'd onboard a sharp new senior engineer to this codebase — the context and traps they'd need that aren't obvious from reading the code. It loads on every session and costs tokens every turn, so signal-per-line is everything. $ARGUMENTS

## Hard rules for the output
- Target under 200 lines; aim for 50–100. Shorter is better for small projects.
- Include ONLY what you cannot infer from reading the code. If a line wouldn't change your behavior, cut it.
- Write imperative, specific, verifiable rules. "Run `pnpm test`" not "test your code". "Use 2-space indentation" not "keep formatting clean".
- Include negative rules (what to NEVER do) alongside positive ones — without them you'll default to the most common pattern, not this project's.
- For any rule that isn't self-explanatory, add a brief reason ("use the repo's Result type, not exceptions — the API layer expects it") so the agent can generalize correctly instead of blindly copying.
- Reserve **IMPORTANT** / **YOU MUST** for the 1–2 genuinely critical rules only. Overusing them destroys their effect.
- NO fluff: no "act as a senior engineer", no personality or motivational lines — near-zero effect, and they bury the rules that matter.
- NO secrets, connection strings, or env values. NO style rules a linter/formatter already enforces (point to .editorconfig / eslint / prettier instead). NO detailed API docs (link them). NO execution plans or checklists (they go stale).
- Never invent a command or convention. Ground every command and rule in a file you actually read. If you can't verify something (the real test command, the deploy step, branch etiquette), ASK me — do not guess.
- Do NOT duplicate Phurti's universal rules (no AI-attributed commits, no banner comments, ask-don't-assume, build-only-what's-needed) — they already apply everywhere via the installed ruleset. This file is for project-specific knowledge only.

## Steps
1. **Detect, then audit.** Check for an existing AGENTS.md / CLAUDE.md (and any init output). If one exists, run in AUDIT mode: read it, judge it against the actual repo, and **leave accurate, useful lines exactly as they are** — don't rewrite what already works. Identify only (a) genuine gaps (a real command, convention, or gotcha that's missing) and (b) stale or bloated lines to trim. If none exists, build one from scratch. Either way, read the repo to find: the package manager and build/test/lint/run commands (package.json scripts, Makefile, pyproject.toml, go.mod, etc.), the directory layout and what each top-level dir is for, the language/framework and versions, and recurring conventions (naming, error handling, test patterns). Use a subagent to investigate if the repo is large.
2. **Confirm the unknowns.** List anything you could not determine for certain — the canonical test command, branch/PR etiquette, "do not touch" directories — and ask me before writing them. Do not fabricate.
3. **Report the audit / draft.** If auditing: show exactly what you'd add and remove, confirm the rest is already good — propose a diff, not a rewrite. If building fresh: draft using the structure below. Keep each section to the few highest-value lines; drop any section that adds no signal.
4. **Wait for approval.** Do NOT write to disk until I approve. If the existing file is already accurate and complete, say so and change nothing.
5. **On approval, write the file at the project root** (`AGENTS.md`, or `CLAUDE.md` on Claude Code). Apply only the agreed additions/removals; preserve everything else verbatim. If rules for one area only matter there, or the file would exceed ~200 lines, propose splitting those into path-scoped rule files and keep the root file a lean index.
6. Tell me to confirm it loaded, and to refine it whenever I correct you twice on the same thing.

## Structure to fill
~~~
# <Project name>

<1–3 bullets: what this project is and its current state. Link the README instead of repeating it.>

## Commands
- Build: <cmd>
- Test: <cmd>   (prefer the single-test command for speed)
- Lint/format: <cmd>
- Run/dev: <cmd>

## Architecture
<3–6 bullets: the layout and how the main pieces fit. Only what isn't obvious from a directory listing.>

## Conventions
- <do: imperative, specific>
- Never <don't: the patterns to avoid in this project>

## Gotchas / pitfalls
<non-obvious behavior, required env vars, "do not edit" dirs, and the specific things an agent tends to get WRONG in this repo — wrong import path, a deprecated module it'll reach for, a pattern that looks fine but breaks here>
~~~
Use `<!-- ... -->` HTML comments for notes meant for humans — most agents strip them before context.
