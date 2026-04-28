#!/usr/bin/env python3
"""Validate a Fit-check TOPSIS matrix without running a ranking."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.topsis import MatrixValidationError, load_matrix, validate_matrix_integrity


def validate_schema_if_available(matrix: dict) -> list[str]:
    """Run JSON Schema validation when the optional jsonschema package is installed."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return ["jsonschema package not installed; skipped JSON Schema validation."]

    schema_path = ROOT / "schemas" / "fit_check_topsis.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(matrix), key=lambda error: list(error.path))
    if not errors:
        return []

    rendered = []
    for error in errors:
        path = ".".join(str(part) for part in error.path) or "<root>"
        rendered.append(f"{path}: {error.message}")
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Fit-check TOPSIS matrix JSON file.")
    parser.add_argument("input", help="Path to matrix JSON")
    parser.add_argument(
        "--strict-schema",
        action="store_true",
        help="Fail if jsonschema is unavailable or if schema validation reports errors.",
    )
    args = parser.parse_args()

    try:
        matrix = load_matrix(args.input)
        validate_matrix_integrity(matrix)
    except MatrixValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    schema_messages = validate_schema_if_available(matrix)
    hard_schema_errors = [msg for msg in schema_messages if not msg.startswith("jsonschema package")]
    if hard_schema_errors or (args.strict_schema and schema_messages):
        print("Schema validation failed:", file=sys.stderr)
        for message in schema_messages:
            print(f"- {message}", file=sys.stderr)
        return 1

    if schema_messages:
        for message in schema_messages:
            print(f"warning: {message}", file=sys.stderr)

    print("ok: matrix is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
