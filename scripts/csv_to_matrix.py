#!/usr/bin/env python3
"""Convert normalized Fit-check CSV files into executable matrix JSON."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.topsis import validate_matrix_integrity


def blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def parse_bool(value: str | None) -> bool | None:
    text = blank_to_none(value)
    if text is None:
        return None
    lowered = text.lower()
    if lowered in {"true", "yes", "y", "1"}:
        return True
    if lowered in {"false", "no", "n", "0"}:
        return False
    raise ValueError(f"Expected boolean value, got: {value}")


def parse_float(value: str | None) -> float | None:
    text = blank_to_none(value)
    if text is None:
        return None
    return float(text)


def split_semicolon(value: str | None) -> list[str]:
    text = blank_to_none(value)
    if text is None:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def read_csv(path: str) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if value is not None and value != []}


def build_matrix(criteria_path: str, options_path: str, scores_path: str) -> dict[str, Any]:
    criteria = []
    for row in read_csv(criteria_path):
        criteria.append(compact({
            "id": blank_to_none(row.get("criterion_id")),
            "name": blank_to_none(row.get("criterion_name")),
            "description": blank_to_none(row.get("description")),
            "priority": blank_to_none(row.get("priority")),
            "points": parse_float(row.get("points")),
            "weight": parse_float(row.get("weight")),
            "direction": blank_to_none(row.get("direction")),
            "is_must": parse_bool(row.get("is_must")),
            "disqualifying_score": parse_float(row.get("disqualifying_score")),
        }))

    options = []
    for row in read_csv(options_path):
        options.append(compact({
            "id": blank_to_none(row.get("option_id")),
            "name": blank_to_none(row.get("option_name")),
            "description": blank_to_none(row.get("description")),
            "assumptions": split_semicolon(row.get("assumptions")),
        }))

    scores = []
    for row in read_csv(scores_path):
        scores.append(compact({
            "option_id": blank_to_none(row.get("option_id")),
            "criterion_id": blank_to_none(row.get("criterion_id")),
            "score": parse_float(row.get("score")),
            "aspect_note": blank_to_none(row.get("aspect_note")),
            "color": blank_to_none(row.get("color")),
            "uncertainty_note": blank_to_none(row.get("uncertainty_note")),
        }))

    matrix = {
        "altitude": {
            "statement": "Generated from normalized CSV files; confirm all options share scope, time horizon, decision type, and success definition.",
            "comparable": True,
        },
        "scale": {"min": 0, "max": 2, "labels": {"0": "Red", "1": "Yellow", "2": "Green"}},
        "criteria": criteria,
        "options": options,
        "scores": scores,
    }
    validate_matrix_integrity(matrix)
    return matrix


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Fit-check CSV templates to matrix JSON.")
    parser.add_argument("--criteria", required=True, help="Path to criteria CSV")
    parser.add_argument("--options", required=True, help="Path to options CSV")
    parser.add_argument("--scores", required=True, help="Path to scores CSV")
    parser.add_argument("--output", required=True, help="Path to write matrix JSON")
    args = parser.parse_args()

    try:
        matrix = build_matrix(args.criteria, args.options, args.scores)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    Path(args.output).write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
