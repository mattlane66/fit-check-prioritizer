import json
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "topsis.py"
EXAMPLE = ROOT / "examples" / "example_matrix.json"


class TopsisRunnerTests(unittest.TestCase):
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

    def test_altitude_gate(self):
        payload = json.loads(EXAMPLE.read_text())
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


if __name__ == "__main__":
    unittest.main()
