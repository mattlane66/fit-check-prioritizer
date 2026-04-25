# TOPSIS method notes

TOPSIS ranks options by comparing each option to an ideal best point and an ideal worst point.

## Fit-check flow

1. Check that options are comparable.
2. Confirm criteria are atomic standards of judgment.
3. Convert Must/Nice labels to points unless explicit weights are supplied.
4. Normalize criterion weights so they sum to 1.
5. Apply must-have gates before ranking by default.
6. Run TOPSIS on the remaining options.
7. Interpret the ranking as structured judgment, not absolute truth.

## Default weights

- Must-have criteria: 5 points.
- Nice-to-have criteria: 1 point.

Normalized weight:

```text
weight = criterion_points / total_points
```

## Default scale

- 0 = Red.
- 1 = Yellow.
- 2 = Green.

For must-have criteria, `0` disqualifies an option by default.

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
