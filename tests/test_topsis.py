import copy
import json
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "topsis.py"
VALIDATOR = ROOT / "scripts" / "validate_matrix.py"
CSV_TO_MATRIX = ROOT / "scripts" / "csv_to_matrix.py"
SENSITIVITY = ROOT / "scripts" / "sensitivity.py"
EXAMPLE = ROOT / "examples" / "example_matrix.json"

sys.path.insert(0, str(ROOT))

from scripts.topsis import MatrixValidationError, topsis, validate_matrix_integrity


class TopsisRunnerTests(unittest.TestCase):
    def load_payload(self):
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_example_runs(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), str(EXAMPLE)],
            check=True,
            capture_output=True,
            text=True,
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["rankings"][0]["option_id"], "o1")
        self.assertAlmostEqual(data["weights_sum_included"], 1.0)

    def test_validate_matrix_script_accepts_example(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(EXAMPLE)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("ok: matrix is valid", proc.stdout)

    def test_sensitivity_script_runs(self):
        proc = subprocess.run(
            [sys.executable, str(SENSITIVITY), str(EXAMPLE)],
            check=True,
            capture_output=True,
            text=True,
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["base_winner"], "o1")
        self.assertGreater(data["variant_count"], 0)

    def test_csv_to_matrix_script_generates_valid_json(self):
        tmp = ROOT / "tests" / "_tmp_matrix_from_csv.json"
        try:
            subprocess.run(
                [
                    sys.executable,
                    str(CSV_TO_MATRIX),
                    "--criteria",
                    str(ROOT / "templates" / "criteria_template.csv"),
                    "--options",
                    str(ROOT / "templates" / "options_template.csv"),
                    "--scores",
                    str(ROOT / "templates" / "scores_template.csv"),
                    "--output",
                    str(tmp),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(tmp.read_text(encoding="utf-8"))
            validate_matrix_integrity(payload)
        finally:
            tmp.unlink(missing_ok=True)

    def test_altitude_gate(self):
        payload = self.load_payload()
        payload["altitude"]["comparable"] = False
        tmp = ROOT / "tests" / "_tmp_bad_altitude.json"
        tmp.write_text(json.dumps(payload), encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(tmp)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("Altitude check failed", proc.stderr)
        finally:
            tmp.unlink(missing_ok=True)

    def test_missing_aspect_note_fails(self):
        payload = self.load_payload()
        del payload["scores"][0]["aspect_note"]
        with self.assertRaises(MatrixValidationError) as ctx:
            topsis(payload)
        self.assertIn("Missing aspect_note", str(ctx.exception))

    def test_numeric_only_aspect_note_fails(self):
        payload = self.load_payload()
        payload["scores"][0]["aspect_note"] = "2"
        with self.assertRaises(MatrixValidationError) as ctx:
            topsis(payload)
        self.assertIn("numeric-only", str(ctx.exception))

    def test_missing_score_cell_fails(self):
        payload = self.load_payload()
        payload["scores"] = payload["scores"][:-1]
        with self.assertRaises(MatrixValidationError) as ctx:
            topsis(payload)
        self.assertIn("Missing score cell", str(ctx.exception))

    def test_duplicate_score_cell_fails(self):
        payload = self.load_payload()
        payload["scores"].append(copy.deepcopy(payload["scores"][0]))
        with self.assertRaises(MatrixValidationError) as ctx:
            topsis(payload)
        self.assertIn("Duplicate score cell", str(ctx.exception))

    def test_score_outside_scale_fails(self):
        payload = self.load_payload()
        payload["scores"][0]["score"] = 3
        with self.assertRaises(MatrixValidationError) as ctx:
            topsis(payload)
        self.assertIn("above scale.max", str(ctx.exception))

    def test_must_have_red_disqualifies_option(self):
        payload = self.load_payload()
        for row in payload["scores"]:
            if row["option_id"] == "o1" and row["criterion_id"] == "c1":
                row["score"] = 0
                row["aspect_note"] = "Fails highest-volume cases because it does not handle intake."
        result = topsis(payload)
        self.assertIn("o1", result["disqualified_options"])
        self.assertNotEqual(result["rankings"][0]["option_id"], "o1")

    def test_all_options_disqualified_fails(self):
        payload = self.load_payload()
        for row in payload["scores"]:
            if row["criterion_id"] == "c1":
                row["score"] = 0
                row["aspect_note"] = "Fails the must-have coverage requirement."
        with self.assertRaises(ValueError) as ctx:
            topsis(payload)
        self.assertIn("No eligible options", str(ctx.exception))

    def test_cost_criterion_prefers_lower_score(self):
        payload = self.load_payload()
        payload["criteria"] = [
            {"id": "c1", "name": "Cost", "priority": "nice", "direction": "cost"}
        ]
        payload["options"] = [
            {"id": "cheap", "name": "Cheap"},
            {"id": "expensive", "name": "Expensive"},
        ]
        payload["scores"] = [
            {"option_id": "cheap", "criterion_id": "c1", "score": 1, "aspect_note": "Requires one week of effort."},
            {"option_id": "expensive", "criterion_id": "c1", "score": 2, "aspect_note": "Requires two weeks of effort."},
        ]
        result = topsis(payload)
        self.assertEqual(result["rankings"][0]["option_id"], "cheap")


if __name__ == "__main__":
    unittest.main()
