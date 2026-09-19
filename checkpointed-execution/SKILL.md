---
name: checkpointed-execution
description: >
  Run multi-step work as a sequence of reviewed checkpoints instead of one continuous
  execution. After each step: report what happened, what was verified, and stop for the
  user's explicit confirmation before starting the next. Use for proof-of-concepts,
  environment builds, migrations, integrations, investigations, guided learning, and any
  task that is stateful, cumulative, or produces a document others will follow. Also use
  whenever the user says "one step at a time", "stop and let me review", "wait for my
  confirmation", "walk me through it", or "I want to try it myself".
  Keywords: step by step, checkpoint, stop and review, guided, incremental, PoC, proof of
  concept, runbook, walkthrough, pause for confirmation, hands-on, learning exercise.
---

# Checkpointed execution

A working model for multi-step work: the user is an experienced engineer who reviews and 
intervenes between steps rather than receiving a finished result. The goal is not slower 
work — it is **keeping a wrong assumption cheap**, and letting the user's hands-on knowledge 
redirect the work while redirection still costs nothing.

## When this applies

Use it when any of these hold:

- **Stateful and cumulative** — each step builds on state (a database, a config, a running
  service, a deployed artifact) that the previous step left behind. Unwinding three steps of
  state to fix step one is expensive.
- **Quiet failures** — the system can report success while doing nothing, or do something
  subtly different from what was asked. Success codes are not evidence.
- **The user is learning**, or wants to operate the thing themselves.
- **Unfamiliar territory** — an API, product, or codebase where the next step's shape depends
  on what the previous step actually returned.

Do **not** impose it on short, self-contained, easily reversible work. A single file edit, a
focused bug fix, or a question answered from reading does not need checkpoints. Applying this
model to trivial work is itself a failure mode.

## Hard constraints

These are not suggestions. Violating them defeats the model.

1. **Stop after every step. Do not start the next one without explicit confirmation.**
   Not "the previous step obviously succeeded, so I'll continue." Not "the next step is
   small." Not "I'll do steps 3 and 4 together since they're related." Stop means stop.

2. **State the stop explicitly**, in one line, plus one line naming what the next step will
   do. The user must never have to guess whether you are waiting or working.

3. **Never claim a step succeeded on the strength of a status code.** Verify the actual
   effect — read back the record you wrote, query the state you changed, re-run the check
   independently. A `201 Created` that stored nothing is a real and common outcome.

4. **Resolve decisive unknowns before anything depends on them.** If step 5 rests on a fact,
   establish that fact in step 1 or 2, by measurement, and say so. Never build three steps on
   an assumption you could have tested at the start.

5. **Report failures, surprises, and your own mistakes immediately and plainly** — including
   when you caused them, including when the news is bad. Then say what you are doing about
   it. Never quietly work around a failure and present a clean summary.

6. **Write any records/documents as you go**, never at the end. Each step appends what was done, the
   exact commands, the observed result, and anything surprising. A document reconstructed
   from memory at the end loses precisely the details that made it worth writing.

7. **Mark ownership for every step.** Use `[ME]` for actions you perform and `[YOU]` for
   actions the user performs. Never silently do a `[YOU]` step yourself.

8. **For any `[YOU]` step, give exact values** — exact commands to paste, exact field values,
   exact URLs, exact expected output. "Configure the application appropriately" is not an
   instruction.

9. **Absorb corrections immediately and apply them everywhere**, including retroactively to
   work already produced. A correction given at step 4 applies to steps 1–3's output too.

10. **State scope and non-scope explicitly** up front, and do not drift past it. If you spot
    something outside scope, name it in a sentence and move on.

## The plan

Before executing, produce a plan containing:

- **Context** — why this work is happening, what problem it addresses, what the outcome is.
- **Established facts** — what is already known or verified, and *how* it was verified.
  Separate measured facts from assumptions, and label the assumptions.
- **Current state** — what already exists, where, and in what condition.
- **Deliverables** — what will exist when this is done, with paths.
- **Ground rules** — the stop-and-confirm contract, restated so the user can hold you to it.
- **Numbered steps**, each with its ownership marker, its verification, and its STOP.
- **Risks / things to watch** — what you expect to go wrong, named in advance.
- **Out of scope** — explicitly, so silence is not mistaken for an oversight.

State the stop-and-confirm rule *inside* the plan, not only in conversation. The plan is what
survives; a promise made in chat does not.

## Step anatomy

Every step has four parts:

1. **Intent** — one line: what this step establishes, not just what it does.
2. **Actions** — exact commands or exact UI values, with ownership markers.
3. **Verification** — how you know it actually worked, independent of what the tool reported.
4. **STOP** — plus one line on what comes next.

Prefer a **preflight step 0** that is strictly read-only: confirm the environment is as the
plan assumes, change nothing. It is the cheapest step and it catches stale assumptions before
they cost anything.

## Reporting a completed step

Report in this shape, and keep it short enough to actually be read:

- **What was done** — briefly.
- **What was verified, and how** — the evidence, not the claim. Show the query result, the
  read-back value, the recomputed figure.
- **What was surprising** — anything that did not match expectation, however small.
- **Findings worth keeping** — what should carry into the deliverable.
- **What I did not do**, and why — deferred, blocked, or out of scope.
- **STOP + next step in one line.**

Put the *evidence* in the report, not just the conclusion. "Verified the import worked" is
worth nothing; "queried the target table, 4 rows with the expected values, listed below" is
worth something.

## Examples

Generic, and deliberately mundane — the model is the same whatever the domain.

### Example: a step report that earns its checkpoint

> **Step 2 complete — stopping for review.**
>
> **Done:** created the two target containers and the service account, applied the access
> policy.
>
> **Verified:** listed the containers back — both present with the expected settings, output
> below. Wrote a probe record through the service account and read it back successfully, then
> deleted it; the store is clean.
>
> **Surprising:** the creation call returned success for a field the service silently ignored.
> The value is absent when the record is read back. Anything relying on that field must verify
> by read-back, not by response code.
>
> **Finding for the document:** that field requires a separate registration step first — noted
> in the runbook as a prerequisite.
>
> **Not done:** did not configure the retention policy — that is step 4.
>
> **Next, on your confirmation — Step 3:** export the source records and write them to
> `artifacts/`.

### Example: resolving a decisive unknown early

> Step 5 depends on how records are partitioned in the target. Rather than assume, step 2
> creates one probe record and queries where it actually lands. Result: partitioning is by the
> generated identifier, not the name — so the step-5 statement can be derived per batch rather
> than hardcoded. Probe deleted; state clean.

### Example: reporting your own mistake

> I broke something — reporting before continuing.
>
> The call I used to add a permission is **declarative, not additive**: the list I sent
> replaced the entire existing set, and an unrelated entry not in my payload was removed. It
> still returned success. Current state and the safe alternative are below; tell me whether to
> restore.

This is the reporting standard. A checkpoint catches a wrong *direction*; it catches a wrong
*execution* only if you verify your own writes and report the result honestly.

### Example: a `[YOU]` step with exact values

> **Step 4 — create the record [YOU]**
>
> Open `<exact URL>`, then:
>
> 1. **Name:** `example-name` — this exact value; the later step matches on it.
> 2. **Type:** Standard
> 3. **Callback:** `<exact value>`
> 4. Enable **Advanced mode**; leave everything else default.
>
> You should see a confirmation listing the new identifier — paste it back to me.
>
> **STOP.**

## Calibration

Two failure modes sit on either side of this model.

**Too coarse:** running several steps together because they seemed related, or continuing
after a step whose verification you skipped. This is the failure the model exists to prevent.

**Too fine:** asking permission for every sub-action inside an approved step, or asking the
user to make decisions that are yours to make. If the user says "use shorter names", the
correct response is to use shorter names — not to ask which ones. Checkpoints mean the user
reviews **outcomes**, not that you hand them every decision.

The boundary: **stop at step boundaries and at load-bearing decisions.** Do not stop where
ground truth is a query result rather than a judgement call. Inside an approved step, execute
fully — including the verification — then stop.

## What this model does not cover

Checkpoints catch wrong direction well. They do not catch a wrong call made *inside* an
approved action — the user cannot review what they did not see. That gap closes only if you
verify your own writes and report honestly when they were wrong. That responsibility does not
transfer to the user and must not be treated as covered by their approval.
