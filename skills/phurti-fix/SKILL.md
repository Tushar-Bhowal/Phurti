---
name: phurti-fix
description: Diagnose and fix a bug at its root cause — reproduce it, trace the real cause, make the smallest correct change, prove it with a regression test. Use for a genuine bug, error, crash, or regression; use /phurti-feature for new functionality or larger changes.
argument-hint: '[the bug — symptom, error message, or how to reproduce it]'
---

# Bug report

## Host conventions
- Use the task in the invoking message and conversation. On Claude Code, supplied skill arguments are also task input; never treat an unexpanded placeholder as a task.
- Invoke skills as `/phurti-name` in Claude Code and `$phurti-name` in Codex CLI/IDE (or select the skill in the app). Adapt the command examples below to the active host.
- Follow `AGENTS.md` on Codex and `CLAUDE.md` on Claude Code, including applicable nested rules. Use the host's available question tool, or ask in chat if it is unavailable in the current mode.
- At the repository root, keep new plans in `.phurti/plans/` and task handoffs in `.phurti/handoff.md`. Read an explicitly supplied legacy `.claude/plans/` file in place; accept legacy `/phurti-*` task tags. At startup, read the shared handoff if present, otherwise `.claude/handoff.md`, and verify it against the current request. Add `.phurti/` to the project's ignore file when creating scratch state.
- Respect approval already given in this conversation. Ask again only when a new decision changes the agreed scope or approach.

Fix the bug at its **root cause**, not the symptom — a symptom patch guarantees it comes back. Follow the global commit and comment rules regardless of whether hooks are active; spend your effort here on getting the diagnosis right. Follow this project's AGENTS.md / CLAUDE.md and conventions.

If no task was supplied, ask me what's broken — the symptom, any error or stack trace, and how to trigger it — before touching anything. For a hard or subtle bug, recommend a higher supported reasoning effort.

If the invoking message points at an audit findings file (`.phurti/plans/audit-findings-*.md`) or just says to fix the audit findings: read that file and work through each **unchecked** item tagged `→ /phurti-fix`, in severity order, ticking it off (`- [x]`) as each is fixed and verified. The file already gives the `file:line` and the concrete fix — don't make me restate them, and don't re-audit. The citation replaces the "reproduce from a vague report" step, but still apply the rest below per item: confirm the root cause from the real code, make the smallest correct change, add a regression test, and show evidence. Leave items tagged `→ /phurti-feature` (new/missing work) for that skill. Run the project's typecheck/build/test suite once at the end across all the fixes.

## 1. Reproduce before you fix
- Give a one-line model recommendation: Claude Code uses Haiku for trivial fixes, Sonnet for localized bugs, Opus for subtle multi-system investigations. Codex uses GPT-6 Luna for clear small fixes, GPT-6.1 Sol for localized debugging, and GPT-6 Astra for difficult root-cause investigations. Recommend an upgrade if the diagnosis grows beyond the initial scope.

Recommend only models available to this user. The Codex names here are a starting policy verified on 2026-11-08, not permanent aliases: consult the host's model list or [current official model guidance](https://learn.chatgpt.com/docs/models) when availability or names are uncertain; never claim you inspected a model list you cannot access. If account availability cannot be checked, label the recommendation conditional and continue on the current model. Start at the supported default effort (Luna High, Astra Light/`low`, Sol's client default), then suggest higher effort for difficult reasoning. Include the model, effort, and one sentence explaining the choice. Codex CLI uses `/model`; IDE/app users use the model picker. Claude Code uses `/model`. Recommend without changing the main session or blocking work on a switch; proceed with the user's chosen model.

- Restate the bug in one line (read through typos), and confirm you can actually trigger it.
- Write a FAILING test that captures it — or, if there's no test setup, a concrete command/steps that reproduce it reliably. You don't understand a bug until you can make it fail on demand.
- If you can't reproduce it, or the report is too vague to pin down, STOP and ask. Never fix a bug you haven't reproduced.

## 2. Find the real root cause — don't stop at the first plausible one
- Read the actual code path involved, in full — not a glance. Shallow investigation is the most common cause of wrong fixes.
- Check what changed near the failure: recent commits, a dependency bump, a config or schema change. A correlated change is often the fastest route to the cause — and the cause may be an external API/library/contract change, not your own code.
- Trace symptom → cause: keep asking "why does that happen?" until you reach a cause that, once fixed, makes the symptom *impossible* — not just rarer.
- State the root cause in a sentence or two and confirm it explains the FULL symptom before you change anything. If the evidence doesn't fit your hypothesis, drop it and keep looking. Don't fix a guess.

## 3. Make the smallest correct fix
- Change only what removes that root cause. No drive-by refactors, renames, or reformatting.
- Mirror existing patterns; don't add libraries or abstractions for a bug fix unless I approve.
- Don't break existing callers or behavior elsewhere — check who depends on what you're touching.

## 4. Prove it's fixed
- The failing test from step 1 now passes; keep it as the regression guard. Add cases for nearby edge cases the bug exposed.
- Run the full suite, the build, and typecheck/lint, and fix every failure. Never weaken or delete a test to go green (the test hook is a heuristic guardrail when installed and enabled).
- Show me the EVIDENCE — the exact commands and their output. No success claims without it.

## 5. Stop and report — commit only when I ask
- When it's fixed and verified, STOP. Give me the root cause (one line), the fix, and the evidence. Do not commit.
- Update `.phurti/handoff.md` after diagnosis, after verification, and when the task lands. Overwrite it; keep it under ~40 lines (goal, done, next steps, decisions, issues, verification). Active SessionStart hooks reload it; Codex hooks require trust. Read it explicitly on resume if hooks are unavailable. Do not rely on compaction to create a narrative summary.
- Commit only when I explicitly say so. After committing, suggest a fresh conversation for unrelated work (`/clear` on Claude Code; a new thread on Codex).

If this turns out to be a missing feature or a multi-file change rather than a bug, say so and point me to `/phurti-feature` instead of forcing it through here.
