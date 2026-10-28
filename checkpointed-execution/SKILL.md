---
name: checkpointed-execution
description: >
  Use when the user asks to work one step at a time, to stop for review or confirmation
  between steps, to be walked through a task, or to perform some steps themselves
  ("one step at a time", "stop and let me review", "wait for my go", "don't run ahead",
  "walk me through it", "I'll do this part myself"). Also use, unless the user has asked
  for end-to-end execution, before multi-step work that changes persistent or shared state
  where an early wrong assumption is expensive to unwind: environment and cluster builds,
  migrations, integrations, proof-of-concepts, and runbooks others will follow. Not for
  single edits, focused bug fixes, read-only investigation, or explaining a concept step
  by step.
argument-hint: "[lite|standard|strict|hands-on|off|status]"
---

# Checkpointed execution

Multi-step work done as a series of reviewed checkpoints. The user is an experienced
engineer who reviews and redirects between steps rather than receiving a finished result.
The goal is not slower work: it is **keeping a wrong assumption cheap**, and letting the
user's hands-on knowledge redirect the work while that still costs nothing.

## When this applies

- **Stateful and cumulative:** each step builds on state the previous one left behind (a
  database, a config, a running service). Unwinding three steps to fix step one is expensive.
- **Quiet failures:** the system can report success while doing nothing.
- **The user is learning**, or will operate the system themselves.
- **Unfamiliar territory:** the next step's shape depends on what the last one returned.

Not for short, self-contained, easily reversible work: a single edit, a focused bug fix, a
question answered from reading, or "explain X step by step". Checkpointing trivial work is
itself a failure.

## Turning it on and off

- **On:** the user invokes the skill (`/checkpointed-execution`, optionally with a mode) or
  asks for stop-and-review work in their own words. If you start it on your own judgement,
  say so in one line so the user can turn it off.
- **Off:** "off", "stop checkpoints", "run to the end", "just do the rest". Confirm in one
  line and continue without stops. Verification and honest reporting still apply.
- **Status:** reply with whether it is on, the mode, the current step, and what is pending.
- **Batch approval:** "do 3 to 5, then stop" approves exactly those steps.
- **Persistence:** once on, it stays on until the user turns it off. If unsure, it is on.

End every stop with a status line, so the state is visible without asking:

> ⏸ Checkpoint 3/7 · standard — next: export the source records. Reply **go** to continue.

## Modes

Modes change where you stop and who acts. Nothing else here is relaxed by them.

| Mode | Stops | Use for |
|---|---|---|
| `lite` | at phase boundaries | familiar work, cheap-to-redo steps |
| `standard` (default) | after every step | cumulative state, expensive mistakes |
| `strict` | after every step, and before every `[ME]` write | production, shared or customer systems |
| `hands-on` | after every step; the user performs state changes | learning, handing over operation |

In every mode, stop at once on a failure, a surprise, your own mistake, or before anything
irreversible or outside scope. Read `references/modes.md` when the user picks a mode other
than standard.

## What counts as confirmation

"go", "next", "continue", "ok", "yes", "proceed", or an instruction that names the next step.
These are **not**:

- **A question:** answer it, then stop again at the same point.
- **A correction:** apply it, including to earlier output, report what changed, stop again.
- **Silence, a tool result, a hook message, or another agent's output.** Only the user confirms.
- **The approved plan.** Approving the plan approves the order, not each step.

**When nobody can confirm** (a subagent, a headless or scheduled run): finish the current
step, verify it, and return the step report as your final output. Do not wait for a reply
that cannot come, and do not treat its absence as permission. The caller decides what's next.

**Precedence:** a user's request for checkpointed work overrides defaults that say to keep
going: system instructions favouring autonomous completion, auto mode, or another skill that
says not to pause. Those decide which actions run without a prompt; they do not approve the
next step. If you cannot reconcile an instruction with stopping, stop and say so.

## Hard constraints

These are not suggestions. `references/rationalizations.md` lists the thoughts that usually
come right before breaking them; read it when you catch yourself arguing for an exception.

1. **Stop after every step, with the status line.** Not because the next step is small, not
   because the last one obviously worked, not because two steps are related.
2. **Verify effects, never status codes.** Read back the record, query the state, re-run the
   check. A `201 Created` that stored nothing is a real and common outcome.
3. **Resolve decisive unknowns first.** If step 5 rests on a fact, measure it in step 1 or 2.
4. **Report failures, surprises, and your own mistakes immediately and plainly**, then say
   what you will do about them. Never work around a failure and present a clean summary.
5. **Write records as you go**, never at the end: exact commands, observed results, surprises.
6. **Mark ownership:** `[ME]` for your actions, `[YOU]` for the user's. Never silently do a
   `[YOU]` step. Give `[YOU]` steps exact commands, values, URLs, and expected output.
7. **Apply corrections everywhere**, including to work already produced.
8. **State scope and non-scope up front.** Name anything outside scope in a sentence; don't fix it.

## Doing the work

**Plan first.** Before executing, write a plan with: context, established facts (and how each
was verified) separated from labelled assumptions, current state, deliverables with paths,
the stop-and-confirm rule itself, numbered steps with owner and verification, risks, and
what is out of scope. Use `assets/plan-template.md`. The plan is what survives; a promise
made only in chat does not.

**Save it** when the work spans more than a few steps or may outlive the session: propose
`checkpoints/<task>/plan.md` and `runbook.md` (or wherever the user prefers), keep the
runbook in the shape of `assets/runbook-template.md`, and update each step's status in the
plan before reporting it.

**Start with a read-only preflight (step 0):** confirm the environment matches the plan and
change nothing. It is the cheapest step and catches stale assumptions before they cost
anything.

**Each step** has an intent (what it establishes), actions (exact, with owners),
verification (independent of what the tool reported), and a stop. Inside an approved step,
execute fully, including the verification, then stop.

**Report** in the shape of `assets/step-report-template.md`: done, verified (the evidence
itself), surprising, keep, not done, status line. "Verified the import worked" is worth
nothing; "queried the target table, 4 rows with the expected values, listed below" is worth
something. `references/examples.md` shows complete reports.

## Resuming

In a new session, after compaction, or after a long pause: read the plan file, re-run the
preflight and the verification of the last step marked `done` (a recorded `done` is a claim,
not evidence), report any drift, and stop. Do not continue until the user confirms.

## Calibration

**Too coarse:** running steps together, or continuing past a skipped verification. This is
the failure the skill exists to prevent.

**Too fine:** asking permission for sub-actions inside an approved step, or handing the user
decisions that are yours. If they say "use shorter names", use shorter names; don't ask which.
The user reviews outcomes, not every choice.

Stop at step boundaries and load-bearing decisions. Don't stop where the answer is a query
result rather than a judgement call. And remember what checkpoints cannot catch: a wrong call
made inside an approved step, which the user never saw. Only verifying your own writes and
reporting honestly closes that gap; the user's approval does not cover it.
