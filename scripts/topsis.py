#!/usr/bin/env python3
"""Dependency-free TOPSIS runner for Fit-check decision matrices."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

DEFAULT_POINTS = {"must": 5.0, "nice": 1.0}
NUMERIC_ONLY_RE = re.compile(r"^\s*[-+]?(?:\d+(?:\.\d*)?|\.\d+)\s*$")


class AltitudeError(ValueError):
    """Raised when the matrix mixes non-comparable options."""


class MatrixValidationError(ValueError):
    """Raised when the matrix contract is incomplete or internally inconsistent."""

    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("Matrix validation failed:\n- " + "\n- ".join(errors))


def load_matrix(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _is_number(value: Any) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number)


def _find_duplicate_ids(rows: List[Dict[str, Any]], label: str) -> List[str]:
    seen = set()
    duplicates = []
    for row in rows:
        row_id = row.get("id")
        if row_id in seen and row_id not in duplicates:
            duplicates.append(row_id)
        seen.add(row_id)
    return [f"Duplicate {label} id: {item}" for item in duplicates]


def validate_aspect_notes(scores: List[Dict[str, Any]]) -> None:
    """Require a descriptive note for every option/criterion score cell."""
    for row in scores:
        option_id = row.get("option_id", "<missing option_id>")
        criterion_id = row.get("criterion_id", "<missing criterion_id>")
        location = f"option={option_id} criterion={criterion_id}"

        if "aspect_note" not in row:
            raise ValueError(f"Missing aspect_note for {location}")

        aspect_note = row["aspect_note"]
        if not isinstance(aspect_note, str):
            raise ValueError(f"aspect_note must be text for {location}")

        stripped = aspect_note.strip()
        if not stripped:
            raise ValueError(f"aspect_note cannot be empty for {location}")

        if NUMERIC_ONLY_RE.match(stripped):
            raise ValueError(f"aspect_note cannot be numeric-only for {location}")


def validate_matrix_integrity(matrix: Dict[str, Any]) -> None:
    """Validate matrix references, completeness, scores, and notes before computation."""
    errors: List[str] = []

    criteria = matrix.get("criteria", [])
    options = matrix.get("options", [])
    scores = matrix.get("scores", [])

    if not isinstance(criteria, list) or not criteria:
        errors.append("At least one criterion is required.")
        criteria = []
    if not isinstance(options, list) or len(options) < 2:
        errors.append("At least two options are required.")
        options = []
    if not isinstance(scores, list):
        errors.append("scores must be a list.")
        scores = []

    for index, criterion in enumerate(criteria):
        if not isinstance(criterion, dict):
            errors.append(f"criteria[{index}] must be an object.")
            continue
        if not criterion.get("id"):
            errors.append(f"criteria[{index}] is missing id.")
        if not criterion.get("name"):
            errors.append(f"criteria[{index}] is missing name.")

    for index, option in enumerate(options):
        if not isinstance(option, dict):
            errors.append(f"options[{index}] must be an object.")
            continue
        if not option.get("id"):
            errors.append(f"options[{index}] is missing id.")
        if not option.get("name"):
            errors.append(f"options[{index}] is missing name.")

    criteria_dicts = [c for c in criteria if isinstance(c, dict)]
    option_dicts = [o for o in options if isinstance(o, dict)]
    errors.extend(_find_duplicate_ids(criteria_dicts, "criterion"))
    errors.extend(_find_duplicate_ids(option_dicts, "option"))

    criterion_ids = {c.get("id") for c in criteria_dicts if c.get("id")}
    option_ids = {o.get("id") for o in option_dicts if o.get("id")}

    scale = matrix.get("scale", {}) if isinstance(matrix.get("scale", {}), dict) else {}
    scale_min = scale.get("min")
    scale_max = scale.get("max")
    if scale_min is not None and not _is_number(scale_min):
        errors.append("scale.min must be numeric when provided.")
    if scale_max is not None and not _is_number(scale_max):
        errors.append("scale.max must be numeric when provided.")
    if _is_number(scale_min) and _is_number(scale_max) and float(scale_min) > float(scale_max):
        errors.append("scale.min cannot be greater than scale.max.")

    seen_cells = set()
    valid_score_rows: List[Dict[str, Any]] = []
    for index, row in enumerate(scores):
        if not isinstance(row, dict):
            errors.append(f"scores[{index}] must be an object.")
            continue
        valid_score_rows.append(row)

        option_id = row.get("option_id")
        criterion_id = row.get("criterion_id")
        cell = (option_id, criterion_id)
        location = f"option={option_id or '<missing option_id>'} criterion={criterion_id or '<missing criterion_id>'}"

        if not option_id:
            errors.append(f"scores[{index}] is missing option_id.")
        elif option_id not in option_ids:
            errors.append(f"Unknown option_id in scores[{index}]: {option_id}")

        if not criterion_id:
            errors.append(f"scores[{index}] is missing criterion_id.")
        elif criterion_id not in criterion_ids:
            errors.append(f"Unknown criterion_id in scores[{index}]: {criterion_id}")

        if option_id and criterion_id:
            if cell in seen_cells:
                errors.append(f"Duplicate score cell for {location}")
            seen_cells.add(cell)

        if "score" not in row:
            errors.append(f"Missing score for {location}")
        elif not _is_number(row["score"]):
            errors.append(f"score must be numeric for {location}")
        else:
            score = float(row["score"])
            if _is_number(scale_min) and score < float(scale_min):
                errors.append(f"score is below scale.min for {location}")
            if _is_number(scale_max) and score > float(scale_max):
                errors.append(f"score is above scale.max for {location}")

    try:
        validate_aspect_notes(valid_score_rows)
    except ValueError as exc:
        errors.append(str(exc))

    for option_id in sorted(option_ids):
        for criterion_id in sorted(criterion_ids):
            if (option_id, criterion_id) not in seen_cells:
                errors.append(f"Missing score cell for option={option_id} criterion={criterion_id}")

    if errors:
        raise MatrixValidationError(errors)


def normalize_criteria(criteria: List[Dict[str, Any]], settings: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    if not criteria:
        raise ValueError("At least one criterion is required.")

    settings = settings or {}
    default_points = {
        "must": float(settings.get("must_points", DEFAULT_POINTS["must"])),
        "nice": float(settings.get("nice_points", DEFAULT_POINTS["nice"])),
    }

    explicit = [c for c in criteria if "weight" in c and c["weight"] is not None]
    if explicit:
        total = sum(float(c.get("weight", 0)) for c in criteria)
        if total <= 0:
            raise ValueError("Explicit weights must sum to a positive number.")
        return [{**c, "normalized_weight": float(c.get("weight", 0)) / total} for c in criteria]

    points = []
    for c in criteria:
        priority = c.get("priority", "nice")
        points.append(float(c.get("points", default_points.get(priority, default_points["nice"]))))
    total_points = sum(points)
    if total_points <= 0:
        raise ValueError("Criterion points must sum to a positive number.")
    return [{**c, "normalized_weight": p / total_points} for c, p in zip(criteria, points)]


def score_lookup(scores: List[Dict[str, Any]]) -> Dict[Tuple[str, str], float]:
    validate_aspect_notes(scores)
    return {(row["option_id"], row["criterion_id"]): float(row["score"]) for row in scores}


def disqualified_options(matrix: Dict[str, Any], criteria: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    scale_min = float(matrix.get("scale", {}).get("min", 0))
    scores = score_lookup(matrix.get("scores", []))
    blockers: Dict[str, List[str]] = {}

    for option in matrix.get("options", []):
        option_id = option["id"]
        for criterion in criteria:
            is_must = criterion.get("priority") == "must" or criterion.get("is_must") is True
            if is_must and criterion.get("gate", True):
                disqualifying = float(criterion.get("disqualifying_score", scale_min))
                score = scores.get((option_id, criterion["id"]))
                if score is None:
                    blockers.setdefault(option_id, []).append(f"missing:{criterion['id']}")
                elif score <= disqualifying:
                    blockers.setdefault(option_id, []).append(criterion["id"])
    return blockers


def topsis(matrix: Dict[str, Any], include_disqualified: bool = False) -> Dict[str, Any]:
    if matrix.get("altitude", {}).get("comparable") is False:
        raise AltitudeError("Altitude check failed: options are not comparable.")

    validate_matrix_integrity(matrix)

    criteria = normalize_criteria(matrix.get("criteria", []), matrix.get("settings", {}))
    options = matrix.get("options", [])
    if len(options) < 2:
        raise ValueError("At least two options are required.")

    scores = score_lookup(matrix.get("scores", []))
    blockers = disqualified_options(matrix, criteria)
    eligible = [o for o in options if include_disqualified or o["id"] not in blockers]
    if not eligible:
        raise ValueError("No eligible options remain after must-have gates.")

    decision: List[List[float]] = []
    for option in eligible:
        row = []
        for criterion in criteria:
            key = (option["id"], criterion["id"])
            if key not in scores:
                raise ValueError(f"Missing score for option={option['id']} criterion={criterion['id']}")
            row.append(scores[key])
        decision.append(row)

    denominators: List[float] = []
    included_criteria: List[Tuple[int, Dict[str, Any]]] = []
    for j, criterion in enumerate(criteria):
        denom = math.sqrt(sum(row[j] ** 2 for row in decision))
        if denom == 0:
            continue
        denominators.append(denom)
        included_criteria.append((j, criterion))
    if not included_criteria:
        raise ValueError("No informative criteria remain after zero-denominator exclusion.")

    raw_weight_sum = sum(c["normalized_weight"] for _, c in included_criteria)
    weighted = []
    for row in decision:
        weighted.append([
            (row[j] / denom) * (criterion["normalized_weight"] / raw_weight_sum)
            for denom, (j, criterion) in zip(denominators, included_criteria)
        ])

    ideal_best = []
    ideal_worst = []
    for col_index, (_, criterion) in enumerate(included_criteria):
        column = [row[col_index] for row in weighted]
        if criterion.get("direction", "benefit") == "cost":
            ideal_best.append(min(column))
            ideal_worst.append(max(column))
        else:
            ideal_best.append(max(column))
            ideal_worst.append(min(column))

    rankings = []
    for option, row in zip(eligible, weighted):
        d_best = math.sqrt(sum((row[j] - ideal_best[j]) ** 2 for j in range(len(included_criteria))))
        d_worst = math.sqrt(sum((row[j] - ideal_worst[j]) ** 2 for j in range(len(included_criteria))))
        denom = d_best + d_worst
        closeness = d_worst / denom if denom else 0.0
        rankings.append({
            "option_id": option["id"],
            "option_name": option.get("name", option["id"]),
            "closeness": closeness,
            "distance_to_ideal": d_best,
            "distance_to_worst": d_worst,
            "disqualified": option["id"] in blockers,
            "blockers": blockers.get(option["id"], []),
        })

    rankings.sort(key=lambda r: r["closeness"], reverse=True)
    for i, row in enumerate(rankings, start=1):
        row["rank"] = i

    near_tie_threshold = float(matrix.get("settings", {}).get("near_tie_threshold", matrix.get("near_tie_threshold", 0.05)))
    near_tie = len(rankings) >= 2 and abs(rankings[0]["closeness"] - rankings[1]["closeness"]) < near_tie_threshold

    criteria_weights = [
        {
            "criterion_id": c["id"],
            "name": c.get("name", c["id"]),
            "normalized_weight": c["normalized_weight"] / raw_weight_sum,
            "priority": c.get("priority", "nice"),
            "direction": c.get("direction", "benefit"),
        }
        for _, c in included_criteria
    ]

    return {
        "status": "ok",
        "rankings": rankings,
        "disqualified_options": blockers,
        "criteria_weights": criteria_weights,
        "weights_sum_included": sum(c["normalized_weight"] for c in criteria_weights),
        "near_tie": near_tie,
        "near_tie_threshold": near_tie_threshold,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TOPSIS on a Fit-check matrix JSON file.")
    parser.add_argument("input", help="Path to matrix JSON")
    parser.add_argument("--output", help="Optional path to write JSON results")
    parser.add_argument("--include-disqualified", action="store_true", help="Include gated-out options in TOPSIS calculation")
    args = parser.parse_args()

    try:
        result = topsis(load_matrix(args.input), include_disqualified=args.include_disqualified)
    except AltitudeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    rendered = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
