# Fit-Check Decision Matrix with TOPSIS

Use this skill when a user wants to compare same-altitude paths, opportunities, experiments, or solution approaches with a Fit-check Decision Matrix and TOPSIS.

## Core principles

- Accuracy beats speed. Never invent missing scores, weights, criteria, or option data.
- Ask only the minimal clarifying questions needed to run or responsibly frame the matrix, with a maximum of 3 questions before proceeding or stopping.
- Separate `VERIFIED`, `ASSUMED`, and `INFERRED` information whenever uncertainty matters.
- Keep narrative aspect notes separate from numeric scoring. Preserve user-provided notes, but never treat notes as numbers.
- Enforce apples-to-apples altitude. If options differ in scope, time horizon, success definition, or decision type, stop and recommend separate matrices.

## When to use

Use for gnarly prioritization where the user has several comparable options and needs structured judgment before deciding what to pursue, shape, prototype, test, or implement.

Good comparison sets include:
- parent opportunities compared against other parent opportunities,
- sibling child opportunities under the same parent,
- solution approaches for one chosen opportunity,
- experiments or spikes that test the same kind of uncertainty,
- paths before shaping when several possible approaches are still half-baked.

Do not use when options are not comparable. Stop and recommend separate matrices if options differ in scope, altitude, time horizon, or success metrics.

## Matrix convention

The human sheet convention is:
- criteria in rows,
- approaches/options/paths in columns,
- each option column includes a one-sentence description,
- each criterion-option cell includes an aspect note plus a score.

The computation convention is normalized:
- options are rows,
- criteria are columns,
- scores are long-form records with `option_id`, `criterion_id`, `score`, and `aspect_note`.

If the user supplies the human sheet layout, transpose/normalize internally and state that you did.

## Start with the frame

Before scoring, reconstruct the decision frame. Capture as much of this as the user can provide:

- Decision from the opportunity identified: what choice is being made?
- Situation / Context: in the last real episode, when the person was trying to do what, in what context, using what?
- Old way: how did they handle it before?
- Trigger / forcing function: what changed that made the old/current way no longer acceptable?
- Constraints / Misfits: what was difficult, risky, slow, expensive, draining, incompatible, or complex?
- Desired outcome: what should the new approach make better?
- Success criteria: how would they know it worked?
- Rejected alternatives: what else was considered, and why did those not win?

If the frame is missing, ask only for the smallest amount needed to compare options responsibly. If the user wants to proceed anyway, label assumptions clearly.

## Empirical requirement prompts

Use these prompts to help extract empirical, technology-agnostic requirements before criteria are finalized:

- Reconstruct the last real episode: "Tell me about the last specific time you were trying to get this done."
- Establish the timeline: "When did you first notice the current way wasn’t good enough?"
- Capture the pre-switch behavior: "What were you doing instead up to that point?"
- Find the forcing function: "What changed that made continuing that way no longer okay?"
- Surface constraints and tradeoffs: "What was difficult, risky, slow, expensive, or draining about it?"
- Clarify the hoped-for improvement: "What exactly did you expect the new approach to make better?"
- Define success concretely: "How would you have known it was working?"
- Check alternatives and non-adoption: "What else did you consider, and why didn’t those win?"

## Startup questions

Ask these only if they block computation or responsible framing. Ask no more than 3 total questions.

1. Are all scores higher-is-better, or do any criteria represent raw costs where lower is better?
2. Which criteria are Must vs Nice, or should the default Must = 5 and Nice = 1 points mapping be used?
3. Are the options comparable at the same altitude: same scope, time horizon, decision type, and success definition?

If the answer can be safely inferred from the provided matrix, proceed and label it as `INFERRED` or `ASSUMED`.

## Required inputs

TOPSIS requires complete numeric values for every ranked option across every included criterion.

Required:
1. Comparable options at the same altitude.
2. A decision statement and desired outcome.
3. Criteria as standards of judgment.
4. Aspect notes for how each option handles each criterion.
5. Numeric scores, or color grades that can be mapped to numeric scores.
6. Weights per criterion, or Must/Nice labels that can be converted to points.
7. Criterion direction: `benefit` or `cost`.
8. Must-have criteria for default gating, or permission to infer them from `must` labels.

Default score mapping:
- Red = 0 = blocker / fails the standard / unacceptable tradeoff.
- Yellow = 1 = workable but meaningfully weak / concern.
- Green = 2 = strong fit / advantage.

The text aspect is what is true; the color/score is the judgment of fitness given the text.

## Altitude check

Before computing, confirm all options are the same kind of thing:
- same parent or same chosen opportunity,
- same time horizon,
- same scope,
- same success definition,
- same decision type.

Rule of thumb: if two options have different scopes, time horizons, or success metrics, split into separate matrices.

This model is best suited for leaf/terminal nodes, such as solutions to shape or experiments to run.

## Criteria rules

Criteria must be:
- standards of judgment, not generic traits,
- atomic: one idea per criterion,
- relevant to the frame,
- consistently phrased,
- positively phrased when using 0/1/2 scores so higher is better.

Useful criterion categories:
- fitness to solve the problem: coverage, reliability, latency, correctness, usability, accessibility, maintainability,
- costs: engineering effort, time, money, opportunity cost,
- risks: privacy/security, failure modes, adoption risk, technical risk,
- compatibility and complexity: integration burden, dependencies, cognitive load, operational complexity,
- purpose-built / reflective fit: how specifically the option matches the frame instead of being generic.

If a criterion includes "and," split it. If a criterion is negatively phrased, rewrite it as a positive criterion and confirm the rewrite before scoring unless the user has already provided clear numeric scores.

## Aspect notes

Each cell should answer: "How does this option handle this criterion?"

Use concrete, checkable content:
- mechanisms: uses X to do Y,
- constraints: requires SSO; adds one extra step,
- dependencies: needs data from system A; creates a new service,
- failure modes: breaks if Z; mitigated by Y,
- assumptions: works only if A is true.

Avoid vibes like "seems good." Avoid yes/no-only, true/false-only, and numeric-only cells. If uncertain, write: "Unknown: needs test."

## Weights

Use Points-to-Percentage unless explicit weights are provided.

Default points:
- Nice-to-have = 1 point.
- Must-have = 5 points.
- Optionally use Must-have = 3 points when the group wants less separation.

Formula:

```text
weight_j = points_j / sum(points_all_criteria)
```

Keep at least 4 decimal places internally. Display rounded weights only with a rounding note.

Practical tip: do not overthink exactness. Weighting is a statement of priorities. Keep it conversational with a small relevant group. Start by marking only the Must Haves before calculating weights.

If criteria are excluded because of missing data or zero denominator, renormalize the remaining weights and report that.

## Must-have gating

Default behavior:
- If an option has a disqualifying score on any must-have criterion, mark it disqualified.
- For 0/1/2 scoring, disqualifying means `score == 0`.
- For other scales, disqualifying means `score == minimum scale value` unless the user specifies a threshold.
- Rank only non-disqualified options by default.
- Compute TOPSIS for disqualified options only if the user explicitly asks for a transparency run.

Any Red (0) on a truly must-have row should trigger: fix the approach or drop it, regardless of TOPSIS rank.

If all options are disqualified, stop and recommend revising options or constraints. Do not relax must-haves without explicit approval.

## Missing data

If any cell is missing or unreadable:
1. Ask only for the missing cells, with at most three questions.
2. If the user cannot provide them, exclude the entire criterion for all options and report it.
3. Exclude an option only with explicit user approval.
4. Do not impute missing values unless the user explicitly requests imputation and the method is stated.

## TOPSIS calculation

Given decision matrix `X` with options `i` and criteria `j`:

1. Confirm all included entries are numeric.
2. Normalize each criterion using vector normalization:

```text
denom_j = sqrt(sum_i x_ij^2)
r_ij = x_ij / denom_j
```

If `denom_j == 0`, exclude the criterion and report that it provides no information.

3. Apply weights:

```text
v_ij = weight_j * r_ij
```

4. Determine ideal best and worst.

For benefit criteria:
```text
A+_j = max_i v_ij
A-_j = min_i v_ij
```

For cost criteria:
```text
A+_j = min_i v_ij
A-_j = max_i v_ij
```

5. Compute distances:

```text
S+_i = sqrt(sum_j (v_ij - A+_j)^2)
S-_i = sqrt(sum_j (v_ij - A-_j)^2)
```

6. Compute closeness:

```text
C_i = S-_i / (S+_i + S-_i)
```

Rank by descending `C_i`.

## Cost vs. benefit

Default: if every criterion is positively phrased and scored 0/1/2 where 2 = best, treat every criterion as `benefit`.

Only use `cost` if the criterion keeps raw numbers where lower is better, such as dollars, weeks, or effort. Preferred workflow: convert raw costs into a 0/1/2 higher-is-better score before TOPSIS.

## Sanity checks

Always report:
- altitude check: all columns/options are truly comparable,
- criteria check: no duplicates and no kitchen-sink rows,
- weight check: normalized weights sum to 1 within rounding tolerance,
- scoring consistency: Green/Yellow/Red mean the same thing across options,
- blocker logic: Red on a must-have triggers fix/drop,
- excluded criteria,
- dominated options,
- double-counting risks when criteria are near duplicates,
- near ties when top coefficients differ by less than 0.05,
- whether the top result is driven by one weird row.

## Large matrix protocol

Use progressive disclosure when:
- `options * criteria > 200`, or
- options > 15, or
- criteria > 15.

For large matrices, do not print full intermediate matrices unless asked. Default to:
- inputs summary: criteria, weights, directions, and must-have gates,
- disqualifications and exclusions,
- TOPSIS results table,
- per-criterion contribution or top-driver summary when available,
- unknowns and assumptions.

Offer follow-up commands:
- Show full score matrix.
- Show normalization and weighted matrix.
- Explain why option A outranks option B.
- Show contribution by criterion.
- Rerun with alternate Must/Nice mapping.

## Decide and choose the next action

After ranking, recommend the next action for the decision altitude:

- Opportunity selection: discovery spike, lightweight experiment, sizing, stakeholder alignment.
- Solution/path selection: shape the approach, prototype, technical spike, implementation plan.
- If uncertainty dominates: define 1-3 assumptions to test, then run the smallest test that can falsify them.

## Output format

Return results in this order:

1. TL;DR: winner among non-disqualified options with TOPSIS closeness.
2. Disqualifications.
3. Frame used:
   - decision statement,
   - baseline / old way,
   - trigger / forcing function,
   - constraints / misfits,
   - desired outcome,
   - success criteria,
   - rejected alternatives.
4. Input status:
   - `VERIFIED`: directly provided by the user or source matrix,
   - `ASSUMED`: filled by default rule or explicit working assumption,
   - `INFERRED`: derived from provided inputs.
5. Verified inputs used:
   - options/paths,
   - criteria,
   - aspect notes or score table slice,
   - weights table,
   - directions.
6. Computation notes:
   - transposition,
   - exclusions,
   - zero denominators,
   - missing-data handling.
7. TOPSIS results:
   - option,
   - closeness coefficient,
   - rank,
   - S+,
   - S-.
8. Interpretation guidance:
   - near ties,
   - key drivers,
   - single-criterion dominance,
   - whether the next move should be select, shape, prototype, spike, or test assumptions.
9. Unknowns and assumptions.
10. Action checklist.

## Important limitation

If scores are ordinal proxies such as Red/Yellow/Green, avoid overinterpreting tiny differences. Use TOPSIS as a structured discussion aid, not as absolute truth.
