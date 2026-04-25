# fit-check-prioritizer

Use this decision matrix for gnarly prioritization problems. It feeds your finished decision matrix sheet with TOPSIS.

This repo contains a Fit-check TOPSIS skill bundle for ranking comparable options with:

- criteria and options,
- per-cell aspect notes,
- numeric score mapping such as Red/Yellow/Green = 0/1/2,
- Points-to-Percentage weights for Must vs. Nice criteria,
- default Must-have gating,
- TOPSIS ranking with transparent math.

## Files

```text
skills/fit-check-topsis/SKILL.md          Agent/LLM skill instructions
skills/fit-check-topsis/skill.json        Minimal skill metadata
schemas/fit_check_topsis.schema.json      JSON input contract
templates/criteria_template.csv           Criteria template
templates/options_template.csv            Options template
templates/scores_template.csv             Long-form scores + aspect notes template
examples/example_matrix.json              Complete example input
scripts/topsis.py                         Dependency-free TOPSIS runner
tests/test_topsis.py                      Basic regression tests
docs/topsis_method.md                     Human-readable method notes
docs/agent_prompt.md                      Copy/paste prompt for non-skill environments
```

## Quick start

Run the example:

```bash
python scripts/topsis.py examples/example_matrix.json
```

Write results to a file:

```bash
python scripts/topsis.py examples/example_matrix.json --output results.json
```

Include disqualified options in the TOPSIS calculation only when you explicitly want a transparency run:

```bash
python scripts/topsis.py examples/example_matrix.json --include-disqualified
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Input model

Use JSON for execution and CSV for collaborative data entry. The recommended workflow is:

1. Confirm all options are the same altitude.
2. Define atomic, positively phrased criteria.
3. Label each criterion `must` or `nice`, or provide explicit criterion weights.
4. Add per-cell aspect notes separately from numeric scores.
5. Score each option/criterion cell numerically.
6. Run TOPSIS on non-disqualified options by default.

## Defaults

- Score scale: `0 = Red`, `1 = Yellow`, `2 = Green`.
- `must` criteria receive 5 points.
- `nice` criteria receive 1 point.
- All criteria are treated as `benefit` unless marked `cost`.
- Must-have gate: score equal to the minimum scale value disqualifies an option on that criterion.
- Near tie threshold: top two closeness coefficients differ by less than `0.05`.

## Notes

TOPSIS is useful for structured judgment, not false precision. If scores are ordinal proxies such as Red/Yellow/Green, interpret small differences cautiously and focus on robust gaps, must-have blockers, and the criteria driving the result.
