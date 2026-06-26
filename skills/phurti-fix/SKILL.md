---
name: phurti-fix
description: Diagnose and fix a bug at its root cause — reproduce it, trace the real cause, make the smallest correct change, prove it with a regression test. Use for a genuine bug, error, crash, or regression; use /phurti-feature for new functionality or larger changes.
argument-hint: [the bug — symptom, error message, or how to reproduce it]
disable-model-invocation: true
---

# Bug: $ARGUMENTS

Fix the bug at its **root cause**, not the symptom — a symptom patch guarantees it comes back. The global rules and hooks already handle commit and comment discipline; spend your effort here on getting the diagnosis right. Follow this project's CLAUDE.md and conventions.

If `$ARGUMENTS` is empty, ask me what's broken — the symptom, any error or stack trace, and how to trigger it — before touching anything. (For a hard or subtle bug, prefix your request with `ultrathink` to reason more deeply.)

## 1. Reproduce before you fix
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
- Run the full suite, the build, and typecheck/lint, and fix every failure. Never weaken or delete a test to go green (the hook blocks this anyway).
- Show me the EVIDENCE — the exact commands and their output. No success claims without it.

## 5. Stop and report — commit only when I ask
- When it's fixed and verified, STOP. Give me the root cause (one line), the fix, and the evidence. Do not commit.
- Commit only when I explicitly say so. After committing, remind me to `/clear`.

If this turns out to be a missing feature or a multi-file change rather than a bug, say so and point me to `/phurti-feature` instead of forcing it through here.
