# fit-check-prioritizer

Use this decision matrix for gnarly prioritization problems. It feeds your finished Fit-check Decision Matrix sheet with TOPSIS. Get a sense of it [here](https://chatgpt.com/g/g-696810f0b98081918c1211ecd38f62a3-fit-check-decision-matrix-with-topsis). You can view a template sheet [here](https://docs.google.com/spreadsheets/d/1ATsYRHJ5M14awkcD8nEF55zM4iwbuXxFpUd4ZbcNUm8/edit?usp=sharing).

Use it for: High-complexity systemic decisions where "gut feel" lacks rigor and traditional scoring lacks depth.
While essential for "Type 1" irreversible commitments—such as Build vs. Buy evaluations, M&A targets, or core infrastructure—its true power lies in resolving strategic stalemates. It acts as a logical guardrail in 0-to-1 development, gating features for "systemic fit" and managing conflicting trade-offs between technical sustainability, speed-to-market, and the customer’s life context. Use it when the path forward is "fuzzy" but the cost of being wrong is high.
For more lightweight approaches, try [this](https://world.hey.com/jason/the-obvious-the-easy-and-the-possible-2e11a3fb) or [this](https://www.producttalk.org/prioritize-opportunities/?srsltid=AfmBOooMepfReyNq_KI_k0MuZxrCjYVbwQx7uwR-547H8qWMnVNv-6mt).

This repo contains a Fit-check TOPSIS skill bundle for ranking comparable idea paths/solution options with:

- a decision frame grounded in a real episode,
- comparable options ideally at the same altitude,
- criteria to eval options,
- per-cell aspect notes to explain how a solution satisfies a criterion,
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
templates/sheet_layout.md                 Human-facing spreadsheet layout guide
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

Use JSON for execution and CSV for normalized data entry. Use `templates/sheet_layout.md` when working in a collaborative spreadsheet with criteria in rows and approaches/options in columns.

The recommended workflow is:

1. Start from the frame: situation/context, old and current way, trigger, misfits, and desired outcome.
2. Confirm all options are at the same altitude.
3. Define atomic, positively phrased criteria.
4. Label each criterion `must` or `nice`, or provide explicit criterion weights.
5. Add per-cell aspect notes separately from numeric scores.
6. Score each option cell numerically.
7. Run TOPSIS on non-disqualified options by default.

## Defaults

- Score scale: `0 = Red`, `1 = Yellow`, `2 = Green`.
- `must` criteria receive 5 points.
- `nice` criteria receive 1 point.
- All criteria are treated as `benefit` unless marked `cost`.
- Must-have gate: score equal to the minimum scale value disqualifies an option on that criterion.
- Near tie threshold: top two closeness coefficients differ by less than `0.05`.

## Notes

TOPSIS is useful for structured judgment, not false precision. If scores are ordinal proxies such as Red/Yellow/Green, interpret small differences cautiously and focus on robust gaps, must-have blockers, and the criteria driving the result.
