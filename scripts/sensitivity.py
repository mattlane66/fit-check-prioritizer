#!/usr/bin/env python3
"""Run lightweight stability checks for a Fit-check TOPSIS matrix."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.topsis import load_matrix, topsis


def winner(matrix: dict[str, Any]) -> str:
    return topsis(matrix)["rankings"][0]["option_id"]


def run_sensitivity(matrix: dict[str, Any]) -> dict[str, Any]:
    base_result = topsis(matrix)
    base_winner = base_result["rankings"][0]["option_id"]
    variants = []

    settings = matrix.get("settings", {})
    for must_points in (3, 5, 7):
        variant = copy.deepcopy(matrix)
        variant.setdefault("settings", dict(settings))["must_points"] = must_points
        variants.append((f"must_points={must_points}", variant))

    for criterion in matrix.get("criteria", []):
        if criterion.get("weight") is not None:
            for factor in (0.8, 1.2):
                variant = copy.deepcopy(matrix)
                for candidate in variant["criteria"]:
                    if candidate["id"] == criterion["id"]:
                        candidate["weight"] = float(candidate["weight"]) * factor
                variants.append((f"weight {criterion['id']} x {factor}", variant))

    scale = matrix.get("scale", {})
    scale_min = float(scale.get("min", 0))
    scale_max = float(scale.get("max", 2))
    for index, score_row in enumerate(matrix.get("scores", [])):
        score = float(score_row["score"])
        for delta in (-1, 1):
            changed = score + delta
            if changed < scale_min or changed > scale_max:
                continue
            variant = copy.deepcopy(matrix)
            variant["scores"][index]["score"] = changed
            option_id = score_row["option_id"]
            criterion_id = score_row["criterion_id"]
            variants.append((f"score {option_id}/{criterion_id} {score:g}->{changed:g}", variant))

    outcomes = []
    stable = 0
    for label, variant in variants:
        try:
            variant_winner = winner(variant)
            same = variant_winner == base_winner
            stable += int(same)
            outcomes.append({"variant": label, "winner": variant_winner, "same_as_base": same})
        except Exception as exc:
            outcomes.append({"variant": label, "error": str(exc), "same_as_base": False})

    total = len(outcomes)
    return {
        "status": "ok",
        "base_winner": base_winner,
        "base_rankings": base_result["rankings"],
        "stable_variant_count": stable,
        "variant_count": total,
        "stability_ratio": stable / total if total else 1.0,
        "flips": [outcome for outcome in outcomes if not outcome.get("same_as_base")],
        "outcomes": outcomes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run lightweight TOPSIS sensitivity checks.")
    parser.add_argument("input", help="Path to matrix JSON")
    parser.add_argument("--output", help="Optional path to write JSON sensitivity report")
    args = parser.parse_args()

    try:
        report = run_sensitivity(load_matrix(args.input))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    rendered = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
