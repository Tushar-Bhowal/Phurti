---
name: phurti-architect
description: Design the architecture for a whole app or a single feature before any code is written — requirements, constraints, 2-3 candidate approaches with trade-offs, a chosen design, risks, and a phased build plan. Produces an architecture doc that /phurti-feature implements. Use for a new app, a large or cross-system feature, or any change big enough that the approach matters more than the code.
argument-hint: '[what to architect — an app, a feature, or a system change]'
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash, Write
---

# Architect: $ARGUMENTS

Design the system above before a line of code. Your job here is the *thinking* — requirements, the right approach, the trade-offs, the risks — captured as an architecture doc that `/phurti-feature` then builds. Do NOT write application code in this run; your only output is the architecture doc. Follow this project's memory file (AGENTS.md / CLAUDE.md) and existing conventions — they override anything here.

This is design, not gold-plating. Architect only what the thing needs — apply the ladder: skip what needn't exist, then the standard library, then a native platform feature, then an already-installed dependency, then the minimum that fully works. The best architecture is the simplest one that meets the real requirements and constraints; don't add layers, services, queues, or abstractions for scale nobody asked for. Propose the lean design and name what you deliberately left out and why.

## 0. Set scope and model
- If `$ARGUMENTS` is empty, ask what I want to architect — a whole app, a feature, or a system change — and the goal in plain words. Restate it as a clear problem statement and confirm before designing.
- State whether this is **whole-app** (greenfield or a major subsystem) or **feature-level** (a feature inside an existing app) — the depth differs. If it turns out to be a small, single-approach change, say so and point me to `/phurti-feature` instead of over-architecting it.
- Real architecture needs Opus (the top reasoning tier). A skill can't pin its own model in every host — the VS Code Claude extension has no `model` field for skills — so I recommend rather than force it: confirm you're on Opus, and if you're on a lighter model switch with `/model` before I go deep. I can't switch it for you.

## 1. Understand the requirements and constraints (ask, don't assume)
- Draw out the real requirements: what it must do, who uses it, the scale / latency / data expectations, and the hard constraints — existing stack, deadlines, team size, budget, compliance. If any of these are unknown and would change the design, STOP and ask me with AskUserQuestion. Never invent a requirement, a scale number, or a constraint.
- For a feature inside an existing app: map what's already there FIRST. Use a subagent to read the relevant parts of the codebase (data model, existing patterns, integration points) and return a short map, so the main context stays clean. The new design must fit existing conventions, not fight them.
- State the requirements and constraints back to me and confirm before you design. Everything downstream depends on getting these right — a wrong assumption here is the most expensive kind of mistake.

## 2. Generate candidate approaches (don't marry the first idea)
- Produce 2-3 genuinely different approaches, not one idea with cosmetic variations. For a substantial design, spawn a subagent per approach to develop each independently and in parallel, each returning a short write-up — then you synthesize. Independent options surface trade-offs a single pass would miss.
- For each approach: the shape (components, data flow, key technology choices), what it's good at, and where it strains.

## 3. Compare and choose (the trade-offs are the point)
- Put the approaches side by side against the requirements and constraints from step 1: fit, complexity, risk, cost, how each handles the parts most likely to change, and how each fails under load or error.
- Pick one and say plainly WHY it wins — and what you're trading away by choosing it. Graft the best ideas from the runners-up. If two are genuinely close, present both and ask me to decide rather than guessing.

## 4. Detail the chosen architecture
- The components and their responsibilities; the data model and the contracts between pieces; how they communicate; where state lives; the exact integration points with existing code.
- Call out the non-obvious decisions and the "why" behind each, so they aren't reversed by mistake later.
- Design in security, data handling, and failure modes from the start — not bolted on: where untrusted input enters, where secrets live, what happens when a dependency is down or slow, how it degrades.
- Name the real risks and unknowns, and how the design contains them — or what to spike/prototype first before committing.

## 5. Phase it into a build plan
- Break the design into an ordered, dependency-aware sequence of tasks, each small enough to be independently buildable, verifiable, and committable: shared foundations (types, schema, helpers) first, then the pieces that consume them, with the riskiest/widest-reaching work later. Flag tasks that touch the highest-risk areas.
- Each task: what it delivers and what "done" looks like, written so a fresh session with zero context can pick it up.

## 6. Write the architecture doc and hand off
- Present the design to me and WAIT for approval before writing anything. If I want changes, revise — don't proceed on an unapproved design, even in auto / auto-accept mode.
- On approval, write it to `.claude/plans/architecture-<name>.md` in the shape under **Output format** below — Markdown with XML-tagged sections, exact paths with the integration seam marked, and a checkbox task list where each task carries a definition of done and is tagged `→ /phurti-feature`. This is the ONLY file you write — no application code. (Make sure `.claude/plans/` is in `.gitignore`.)
- Then hand me the tiny message to paste: `/phurti-feature build the architecture in .claude/plans/architecture-<name>.md`. The detail lives in the file, so I never re-type it — `/phurti-feature` reads it and builds the phases in order.

If anything about the requirements, scale, or constraints is unclear at any point, STOP and ask a specific question rather than designing on a guess. Tell me what you're doing at each phase boundary, and if you catch yourself about to assume something load-bearing, ask instead.

## Output format for the architecture doc

Write Markdown with the XML-tagged sections below — Claude keys off the tags, the prose stays readable. Fill every section, keep each tight, and ground every path in the real repo. This is a shape to aim for, not a rigid mold: a data pipeline or a refactor won't look identical, so adapt the sections to the design rather than forcing the design into the sections.

~~~
# Architecture — <name>

<requirements>
- What it must do, who uses it, the scale / latency / data expectations.
- Hard constraints (stack, deadline, compliance). Flag anything you're assuming AS an assumption.
</requirements>

<decision>
The chosen approach in 2-3 lines — and what you rejected and why. The trade-off is the point.
</decision>

<file-map>
Exact paths from the real repo, with the integration seam marked explicitly.

Existing — where it plugs in:
  path/to/existing/file.ext
    → functionName()   ← seam: call newThing() here

New — to create (follows the existing pattern):
  path/to/new/area/
    ├── service.ext     (what it does)
    └── route.ext       (auth: …)
</file-map>

<design>
Components and responsibilities; the data model and contracts; where state lives; failure modes;
where untrusted input enters and where secrets live. Use real code snippets for the non-obvious
contracts, not prose.
</design>

<risks>
The real unknowns and how the design contains them — or what to spike first.
</risks>

<tasks>
Ordered, atomic, foundations first. Each is independently buildable and has a definition of done.
Build one or a few at a time — never "do all of them at once".
- [ ] 1. <task> — files: … — done when: … → /phurti-feature
- [ ] 2. <task> — files: … — done when: … → /phurti-feature
</tasks>
~~~

Worked example of `<file-map>` and `<tasks>` (the level of specificity to aim for):

~~~
<file-map>
Existing — where it plugs in:
  apps/api/src/features/subscription/admin/controller/manualPaymentVerificationController.js
    → approveVerification()   ← seam: call generateInvoice() after approval (already atomic)

New — to create (follows the existing feature pattern):
  apps/api/src/features/invoices/
    ├── services/invoiceGeneratorService.js   (billingSnapshot → HTML → PDF → S3)
    └── routes/invoiceRoutes.js               (auth: user, owner-check)
  shared/src/models/invoice.js
</file-map>

<tasks>
- [ ] 1. Add invoice + invoiceTemplate models — files: shared/src/models/{invoice,invoiceTemplate}.js — done when: schemas defined and exported → /phurti-feature
- [ ] 2. invoiceGeneratorService — files: apps/api/src/features/invoices/services/invoiceGeneratorService.js — done when: a billingSnapshot produces a PDF in S3, unit-tested → /phurti-feature
- [ ] 3. Wire generateInvoice() into approveVerification() — done when: approving a manual payment creates the invoice atomically → /phurti-feature
</tasks>
~~~
