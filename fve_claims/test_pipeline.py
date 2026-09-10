"""Exercise actual scoring and analysis entry points using a tiny fake AR, no model weights."""
import contextlib
import importlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from atomic import sentence_spans


class PipelineTest(unittest.TestCase):
    def test_score_and_analyze(self):
        source = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / "out").mkdir()
            z = "The text is English. Next comes A or B."
            prefix = "An English sentence."
            tasks = {0: dict(prefix_text=prefix, explanation=z, split="dev", sentences=sentence_spans(z))}
            claims = []
            for i, (kind, subtype, truth) in enumerate((("theme", "language", "true"), ("forecast", "continuation", "unsupported"))):
                claims.append(dict(protocol="atomic-v1", pilot_id=0, claim_id=i, proposition=tasks[0]["sentences"][i]["text"],
                                   av_spans=[tasks[0]["sentences"][i]], type=kind, subtype=subtype, truth=truth,
                                   prefix_evidence=[dict(start=0, end=len(prefix), text=prefix)] if i == 0 else [],
                                   rationale="prefix: English; AV: language or forecast", review_flag=False))
            deletions = [dict(protocol="atomic-v1", pilot_id=0, claim_id=i, proposition=claims[i]["proposition"], original_explanation=z,
                              deleted_text=tasks[0]["sentences"][1-i]["text"], removes_claim=True,
                              preserves_other_propositions=True, reviewer="test", rationale="Independent clauses.") for i in range(2)]
            for name, rows in (("02_atoms_7b.jsonl", claims), ("04_deletions_7b.jsonl", deletions),
                               ("01_av_7b.jsonl", [dict(pilot_id=0, split="dev", parse_ok=True, explanation=z)])):
                (root / name).write_text("".join(json.dumps(row) + "\n" for row in rows))
            np.savez(root / "out/acts_7b.npz", h20=np.array([[1., 0.], [0., 1.]]), pilot_id=[0, 1])
            class AR:
                def __init__(self): self.n_forward = 0
                def predict(self, text):
                    self.n_forward += 1
                    value = np.array([1., 0.]) if text == z else np.array([0., 1.])
                    return types.SimpleNamespace(numpy=lambda: value)
                def free(self): pass
            def settings(step, **kw):
                (root / f"{step}_settings.json").write_text(json.dumps(kw)); return kw
            common = types.ModuleType("common")
            common.HERE = root; common.OUT = root / "out"; common.Path = Path
            common.FVE_DENOM_RELEASED_7B = 0.7335
            common.read_jsonl = lambda path: [json.loads(line) for line in Path(path).read_text().splitlines()]
            common.settings = settings
            common.finish = lambda step, data, **kw: settings(step, **{**data, **kw})
            common.git_hash = lambda: "test"
            common.fve = lambda cos, denom: 1 - 2 * (1 - cos) / denom
            common.L = types.SimpleNamespace(AR=AR, cos=lambda a, b: float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))), log=lambda message: None)
            task_module = importlib.import_module("02_claims")
            def load(name):
                spec = importlib.util.spec_from_file_location("test_" + name, source / f"{name}.py")
                mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
            with patch.dict(sys.modules, {"common": common}), patch.object(task_module, "build_tasks", return_value=tasks), contextlib.redirect_stdout(io.StringIO()):
                score = load("04_score")
                with patch.object(sys, "argv", ["04_score.py"]): score.main()
                result = pd.read_csv(root / "04_atomic_scores_7b.csv")
                self.assertEqual(result.claim_id.tolist(), [0, 1])
                np.testing.assert_allclose(result.fve_drop_released, 2 / 0.7335)
                analysis = load("05_analyze")
                with patch.object(sys, "argv", ["05_analyze.py"]): analysis.main()
                report = (root / "05_atomic_summary_all.md").read_text()
                self.assertIn("Claims scored 2", report)
                self.assertIn("| forecast | n=0 | n=0 |", report)
                self.assertTrue((root / "fig/fve_drop_atomic_7b_all.png").exists())
                changed = [dict(c) for c in claims]
                changed[0]["proposition"] = "A different claim."
                (root / "02_atoms_7b.jsonl").write_text("".join(json.dumps(c) + "\n" for c in changed))
                with patch.object(sys, "argv", ["05_analyze.py"]), self.assertRaisesRegex(ValueError, "changed since scoring"):
                    analysis.main()
                # Restore valid labels and exercise the full report with sparse cells.
                (root / "02_atoms_7b.jsonl").write_text("".join(json.dumps(c) + "\n" for c in claims))
                full_report = load("06_statistics")
                full_report.HERE = root
                full_report.main()
                self.assertTrue((root / "06_baseline_report.md").exists())
                coverage = pd.read_csv(root / "06_coverage.csv")
                self.assertEqual(int(coverage[coverage.split == "all"].scored.sum()), 2)
                # Never silently discard scores when replacement labels omit a claim.
                (root / "02_atoms_7b.jsonl").write_text(json.dumps(claims[0]) + "\n")
                with patch.object(sys, "argv", ["05_analyze.py"]), self.assertRaisesRegex(ValueError, "no labels"):
                    analysis.main()
                # Reject unreviewed edits before constructing AR.
                (root / "02_atoms_7b.jsonl").write_text("".join(json.dumps(c) + "\n" for c in claims))
                deletions[0]["preserves_other_propositions"] = False
                (root / "04_deletions_7b.jsonl").write_text("".join(json.dumps(d) + "\n" for d in deletions))
                with patch.object(common.L, "AR", side_effect=AssertionError("AR must not load")), patch.object(sys, "argv", ["04_score.py"]), self.assertRaisesRegex(ValueError, "needs review"):
                    score.main()


if __name__ == "__main__": unittest.main()
