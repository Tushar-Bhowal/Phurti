# Phurti — agent rules

Phurti is a portable rule + workflow set for AI coding agents. The block below is the always-on ruleset; it applies in every session on every agent that reads this file. It is the single source of truth — the per-agent adapter files are generated from it (`scripts/build-adapters.sh`).

<!-- >>> phurti rules >>> -->
## Rules

- Start files with code. Never add a descriptive header/banner comment block at the top of a new or edited file ("This file does X", "ported from Y", "scoped as Z"), and never write comments that narrate the change ("logic unchanged, only markup redesigned", "refactored to…", "updated per request"). That belongs in the commit message and git history. Comment only where a specific line is genuinely non-obvious.
- Commit messages read like a human engineer wrote them. Never mention AI, an assistant, or which model was used; no "Generated with…" footer; no co-author trailer.
- When a requirement, file, value, or behavior is unclear, ask a specific question instead of guessing or inventing it.

## Build only what's needed

Before writing code, stop at the first rung that holds:

1. Does this need to exist? — if not, don't build it.
2. Does the language or standard library already do it? — use that.
3. Is there a native platform feature for it? — use that.
4. Is it an already-installed dependency? — use that.
5. Can it be one line, or a few? — keep it that small.
6. Only then: the minimum that fully works.

Small because it's necessary, not golfed — never cut input validation, error handling, security, or accessibility to shrink code.
<!-- <<< phurti rules <<< -->
