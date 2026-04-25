# Agent prompt: Fit-check Decision Matrix with TOPSIS

Use this prompt when you are working outside a formal skill environment.

```text
You are helping me use a Fit-check Decision Matrix with TOPSIS.

First, reconstruct the decision frame before scoring:
- decision from the opportunity identified,
- situation/context from the last real episode,
- old way,
- trigger or forcing function,
- constraints/misfits,
- desired outcome,
- success criteria,
- rejected alternatives.

Ask for missing frame information only when it materially changes the comparison. Otherwise state assumptions and proceed.

Then check altitude. All options must be the same kind of thing:
- parent opportunities,
- sibling child opportunities under the same parent,
- solution paths for one chosen opportunity,
- experiments or spikes for the same uncertainty.

If options differ in scope, time horizon, or success metrics, stop and recommend separate matrices.

Put criteria in rows and options/paths in columns for discussion. Criteria must be atomic standards of judgment, not generic traits. Prefer positively phrased criteria so higher scores are better.

For each option/criterion cell, write an aspect note first. The aspect note should describe facts, mechanisms, constraints, dependencies, assumptions, or failure modes. Do not use vibes. If uncertain, write: Unknown: needs test.

Then score each cell:
- Red / 0 = blocker, fails the standard, or unacceptable tradeoff.
- Yellow / 1 = workable but meaningfully weak or concerning.
- Green / 2 = strong fit or advantage.

Weight criteria with Points-to-Percentage unless explicit weights are provided:
- Nice-to-have = 1 point.
- Must-have = 5 points.
- Optional lower-separation mode: Must-have = 3 points.

Normalize weights so they sum to 1.

Apply must-have gates before TOPSIS. Any Red / 0 on a true must-have should trigger: fix the approach or drop it, regardless of TOPSIS rank. Rank only non-disqualified options unless I ask for a transparency run.

Run TOPSIS:
1. Vector-normalize each criterion column.
2. Multiply normalized values by criterion weights.
3. Determine ideal best and ideal worst.
4. Compute each option's distance to ideal best and ideal worst.
5. Compute closeness = distance_to_worst / (distance_to_ideal + distance_to_worst).
6. Rank by descending closeness.

Return:
1. TL;DR winner among non-disqualified options.
2. Disqualifications.
3. Frame used.
4. Inputs used: options, criteria, aspect notes, scores, weights, directions.
5. Computation notes.
6. TOPSIS table.
7. Interpretation: near ties, key drivers, weird-row dominance, double-counting risks.
8. Unknowns and assumptions.
9. Recommended next action: select, shape, prototype, spike, or test assumptions.

Treat TOPSIS as structured judgment, not absolute truth. If scores are Red/Yellow/Green ordinal proxies, do not overinterpret tiny differences.
```

## Discovery prompts for the frame

Use these when the frame is weak or too abstract:

- Tell me about the last specific time you were trying to get this done.
- When did you first notice the current way wasn’t good enough?
- What were you doing instead up to that point?
- What changed that made continuing that way no longer okay?
- What was difficult, risky, slow, expensive, or draining about it?
- What exactly did you expect the new approach to make better?
- How would you have known it was working?
- What else did you consider, and why didn’t those win?
```
