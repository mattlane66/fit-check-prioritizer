# Fit-Check Decision Matrix with TOPSIS

Use this skill when a user wants to rank comparable options using a Fit-check Decision Matrix and TOPSIS.

## When to use

Use for multi-criteria prioritization where the user has:
- comparable options at the same altitude,
- criteria that define standards of judgment,
- per-cell notes/aspects,
- numeric scores or color grades that can be mapped to numeric scores,
- weights or Must/Nice labels.

Do not use when options are not comparable. Stop and recommend separate matrices if options differ in scope, altitude, time horizon, or success metrics.

## Matrix convention

For computation:
- options are rows,
- criteria are columns.

If the user supplies criteria as rows and options as columns, transpose internally and state that you did.

## Required inputs

TOPSIS requires complete numeric values for every ranked option across every included criterion.

Required:
1. Numeric score matrix.
2. Weights per criterion, or Must/Nice labels that can be converted to points.
3. Criterion direction: `benefit` or `cost`.
4. Must-have criteria for default gating, or permission to infer them from `must` labels.

Default score mapping:
- Red = 0 = blocker or unacceptable fit.
- Yellow = 1 = workable but weak or concerning.
- Green = 2 = strong fit or advantage.

If only colors are provided, propose this mapping and label it as assumed.

## Altitude check

Before computing, confirm all options are the same kind of thing:
- sibling opportunities,
- sibling solution approaches for the same opportunity,
- same time horizon,
- same scope,
- same success definition.

If mixed altitude, stop. Suggest separate matrices.

## Criteria rules

Criteria must be:
- standards of judgment, not generic traits,
- atomic: one idea per criterion,
- positively phrased when using 0/1/2 scores so higher is better.

If a criterion includes “and,” split it.
If a criterion is negatively phrased, rewrite it as a positive criterion and confirm the rewrite before scoring unless the user has already provided clear numeric scores.

## Weights

Use Points-to-Percentage unless explicit weights are provided.

Default points:
- Nice-to-have = 1 point.
- Must-have = 5 points.

Formula:

```text
weight_j = points_j / sum(points_all_criteria)
```

Keep at least 4 decimal places internally. Display rounded weights only with a rounding note.

If criteria are excluded because of missing data or zero denominator, renormalize the remaining weights and report that.

## Must-have gating

Default behavior:
- If an option has a disqualifying score on any must-have criterion, mark it disqualified.
- For 0/1/2 scoring, disqualifying means `score == 0`.
- For other scales, disqualifying means `score == minimum scale value` unless the user specifies a threshold.
- Rank only non-disqualified options by default.
- Compute TOPSIS for disqualified options only if the user explicitly asks for a transparency run.

If all options are disqualified, stop and recommend revising options or constraints. Do not relax must-haves without explicit approval.

## Missing data

If any cell is missing or unreadable:
1. Ask only for the missing cells, with at most three questions.
2. If the user cannot provide them, exclude the entire criterion for all options and report it.
3. Do not impute missing values unless the user explicitly requests imputation and the method is stated.

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

## Sanity checks

Always report:
- whether weights sum to 1 within rounding tolerance,
- disqualified options and the must-have criteria causing disqualification,
- excluded criteria,
- dominated options,
- double-counting risks when criteria are near duplicates,
- near ties when top coefficients differ by less than 0.05.

## Output format

Return results in this order:

1. TL;DR: winner among non-disqualified options with TOPSIS closeness.
2. Disqualifications.
3. Verified inputs used:
   - options,
   - criteria,
   - score table or slice,
   - weights table,
   - directions.
4. Computation notes:
   - transposition,
   - exclusions,
   - zero denominators,
   - missing-data handling.
5. TOPSIS results:
   - option,
   - closeness coefficient,
   - rank,
   - S+,
   - S-.
6. Interpretation guidance:
   - near ties,
   - key drivers,
   - single-criterion dominance.
7. Unknowns and assumptions.
8. Action checklist.

## Important limitation

If scores are ordinal proxies such as Red/Yellow/Green, avoid overinterpreting tiny differences. Use TOPSIS as a structured discussion aid, not as absolute truth.
