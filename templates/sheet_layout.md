# Human sheet layout

Use this layout for collaborative spreadsheet work before converting to the normalized JSON/CSV format used by `scripts/topsis.py`.

## Header

```text
Decision we are making from the opportunity identified: <decision>
```

## Frame block

```text
FRAME
Situation / Context
In the last real episode, when the person was trying to ___, in the context of ___, they were using ___.

Old way
Before this, they handled it by ___.

Trigger / forcing function
The situation changed when ___, which made continuing the old/current way no longer acceptable.

Constraints / Misfits
The key problems were ___, ___, and ___.

Desired outcome
They wanted the new approach to make ___ better.

Success criteria
They would judge it worked if ___.

Optional: Rejected alternatives
They also considered ___, but rejected them because ___.
```

## Matrix shape

Use this human-facing shape:

```text
                     Approach title 1       Approach title 2       Approach title n
Description          One sentence           One sentence           One sentence

Criterion 1
Must Have: Y/N
Weight: <weight>     Aspect + Score         Aspect + Score         Aspect + Score

Criterion 2
Must Have: Y/N
Weight: <weight>     Aspect + Score         Aspect + Score         Aspect + Score
```

## Cell format

Each option/criterion cell should contain both:

```text
Aspect: <succinct description of how the approach handles the criterion>
Score: 0, 1, or 2
```

Aspect notes should describe mechanisms, assumptions, parameters, dependencies, constraints, failure modes, or unknowns. Avoid yes/no-only, true/false-only, and numeric-only cell content.

## Scoring

```text
Red = 0 = blocker / fails the standard / unacceptable tradeoff
Yellow = 1 = workable but meaningfully weak / concern
Green = 2 = strong fit / advantage
```

Keep the aspect text factual. Put subjective judgment in the color/score.

## Weighting

Use Points-to-Percentage:

```text
Nice-to-have = 1 point
Must-have = 5 points
weight = criterion_points / sum(all_criterion_points)
```

Optionally use 3 points for Must-have when you want less separation.

## Conversion to runner format

The spreadsheet is human-friendly. The runner expects normalized data:

- `options`: one row/object per option.
- `criteria`: one row/object per criterion.
- `scores`: one row/object per option + criterion pair, with `aspect_note` and `score`.

Use the CSV templates for normalized input or convert the sheet into `examples/example_matrix.json` shape.
