# TOPSIS method notes

TOPSIS ranks options by comparing each option to an ideal best point and an ideal worst point.

Use it here as the calculation layer for a Fit-check Decision Matrix. The judgment still comes from the frame, criteria, aspect notes, scores, and weights.

## Fit-check flow

1. Pick the altitude you are comparing.
2. Reconstruct the decision frame.
3. Confirm criteria are atomic standards of judgment.
4. Put paths/options in columns for human discussion.
5. Fill cells with aspect notes: facts, mechanisms, constraints, dependencies, assumptions, or failure modes.
6. Color-grade each cell and map colors to scores.
7. Convert Must/Nice labels to points unless explicit weights are supplied.
8. Normalize criterion weights so they sum to 1.
9. Apply must-have gates before ranking by default.
10. Run TOPSIS on the remaining options.
11. Interpret the ranking as structured judgment, not absolute truth.

## Altitude

All options must be comparable. Good comparison sets include:

- parent opportunities,
- sibling child opportunities under the same parent,
- solution paths for one chosen opportunity,
- experiments or spikes for the same kind of uncertainty.

If two options differ in scope, time horizon, or success metric, split them into separate matrices. This model works best for leaf or terminal nodes, such as solutions to shape or experiments to run.

## Frame

A strong matrix starts from a decision and desired outcome, not from arbitrary criteria.

Capture:

- decision from the opportunity identified,
- situation/context from the last real episode,
- old way,
- trigger or forcing function,
- constraints/misfits,
- desired outcome,
- success criteria,
- rejected alternatives.

Useful prompts:

- Tell me about the last specific time you were trying to get this done.
- When did you first notice the current way wasn’t good enough?
- What were you doing instead up to that point?
- What changed that made continuing that way no longer okay?
- What was difficult, risky, slow, expensive, or draining about it?
- What exactly did you expect the new approach to make better?
- How would you have known it was working?
- What else did you consider, and why didn’t those win?

## Criteria

Criteria are standards of judgment, not generic traits and not an exhaustive requirements list.

Draw from:

- fitness to solve the problem: coverage, reliability, latency, correctness, usability, accessibility, maintainability,
- costs: engineering effort, time, money, opportunity cost,
- risks: privacy/security, failure modes, adoption risk, technical risk,
- compatibility and complexity: integration burden, dependencies, cognitive load, operational complexity,
- purpose-built / reflective fit: how specifically the option matches the frame.

Keep each criterion atomic. If it has "and," split it. Prefer positive phrasing so that higher scores are always better.

## Aspect notes

Each option/criterion cell should answer: how does this option handle this criterion?

Good aspect notes include:

- mechanisms,
- constraints,
- dependencies,
- failure modes,
- assumptions,
- unknowns that need testing.

The aspect text should stay factual. The score/color is the judgment of fitness.

## Default weights

Use Points-to-Percentage unless explicit weights are supplied.

- Must-have criteria: 5 points.
- Nice-to-have criteria: 1 point.
- Optional lower-separation mode: Must-have = 3 points.

Normalized weight:

```text
weight = criterion_points / total_points
```

The weighting is a statement of priorities. Do not overinterpret the exact decimals.

## Default scale

- Red / 0 = blocker, fails the standard, or unacceptable tradeoff.
- Yellow / 1 = workable but meaningfully weak or concerning.
- Green / 2 = strong fit or advantage.

For must-have criteria, `0` disqualifies an option by default.

## Cost vs benefit

Default recommendation: phrase every criterion positively and use 0/1/2 scoring where 2 is best. Then all criteria are `benefit` criteria.

Only use `cost` if you keep raw numbers where lower is better, such as dollars, weeks, or effort. For this workflow, it is usually cleaner to convert raw costs into a 0/1/2 higher-is-better score first.

## TOPSIS steps

1. Vector-normalize each criterion column.
2. Multiply normalized values by criterion weights.
3. Find ideal best and ideal worst values.
4. Compute each option's distance to ideal best and ideal worst.
5. Compute closeness:

```text
closeness = distance_to_worst / (distance_to_ideal + distance_to_worst)
```

Higher closeness is better.

## Interpretation warnings

When scores are ordinal proxies such as Red/Yellow/Green, small TOPSIS differences should not be treated as precise. Pay more attention to robust gaps, disqualifying criteria, and which criteria drive the result.

If the top two results differ by less than 0.05, treat it as a near tie and decide by constraints, sequencing, or a quick test.

If the winner is driven by one strange criterion, inspect that row before deciding.

## Next action after ranking

- Opportunity selection: discovery spike, lightweight experiment, sizing, stakeholder alignment.
- Solution/path selection: shape the approach, prototype, technical spike, implementation plan.
- Uncertainty-dominated result: define 1-3 assumptions to test and run the smallest falsifying test.
