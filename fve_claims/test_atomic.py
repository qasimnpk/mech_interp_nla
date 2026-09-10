import copy
import importlib
import unittest
from atomic import sentence_spans, validate_claims, validate_deletions


class AtomicTests(unittest.TestCase):
    def setUp(self):
        self.z = 'A died in 1969. A died in 1969. A died in 1971.'
        self.tasks = {0: {"prefix_text": "A died in 1969.", "explanation": self.z, "sentences": sentence_spans(self.z)}}
        self.claim = dict(protocol="atomic-v1", pilot_id=0, claim_id=0, proposition="A died in 1969.",
                          av_spans=[dict(s) for s in self.tasks[0]["sentences"][:2]], type="detail", subtype="date",
                          truth="true", prefix_evidence=[dict(start=0, end=15, text="A died in 1969.")],
                          rationale="prefix: death in 1969; AV: death in 1969", review_flag=False)
    def test_repeated_and_conflicting_claims(self):
        other = copy.deepcopy(self.claim)
        other.update(claim_id=1, proposition="A died in 1971.", truth="false", related="related", av_spans=[self.tasks[0]["sentences"][2]])
        self.assertEqual(len(validate_claims([self.claim, other], self.tasks)), 2)
    def test_reject_stale_span(self):
        self.claim["av_spans"][0]["start"] = 1
        with self.assertRaises(ValueError): validate_claims([self.claim], self.tasks)
    def test_reject_duplicate_atom(self):
        other = copy.deepcopy(self.claim); other["claim_id"] = 1
        with self.assertRaises(ValueError): validate_claims([self.claim, other], self.tasks)
    def test_forecasts_and_tokens(self):
        self.claim.update(type="forecast", subtype="continuation")
        with self.assertRaises(ValueError): validate_claims([self.claim], self.tasks)
        self.claim["truth"] = "irrelevant"
        validate_claims([self.claim], self.tasks)
        self.claim.update(type="detail", subtype="final_token", truth="true")
        with self.assertRaises(ValueError): validate_claims([self.claim], self.tasks)
        self.claim["review_flag"] = True
        validate_claims([self.claim], self.tasks)
        self.claim.update(subtype="date", truth="false")
        with self.assertRaises(ValueError): validate_claims([self.claim], self.tasks)
        self.claim["related"] = "related"
        validate_claims([self.claim], self.tasks)
    def test_prefix_evidence_required(self):
        self.claim["prefix_evidence"] = []
        with self.assertRaises(ValueError): validate_claims([self.claim], self.tasks)
    def test_reviewed_deletion(self):
        d = dict(protocol="atomic-v1", pilot_id=0, claim_id=0, proposition=self.claim["proposition"], original_explanation=self.z,
                 deleted_text="A died in 1971.", removes_claim=True, preserves_other_propositions=True,
                 reviewer="test", rationale="Removed both occurrences; kept conflicting claim.")
        validate_deletions([d], [self.claim], self.tasks)
        d["preserves_other_propositions"] = False
        with self.assertRaises(ValueError): validate_deletions([d], [self.claim], self.tasks)
        d["preserves_other_propositions"] = True; d["original_explanation"] = "stale"
        with self.assertRaises(ValueError): validate_deletions([d], [self.claim], self.tasks)
    def test_short_and_quoted_context(self):
        text = 'Yes. “A. B.” Next.\nX'
        spans = sentence_spans(text)
        self.assertEqual([s["text"] for s in spans], ['Yes.', '“A. B.” Next.', 'X'])
        for s in spans: self.assertEqual(text[s["start"]:s["end"]], s["text"])
    def test_real_tasks_blind_and_exact(self):
        tasks = importlib.import_module("02_claims").build_tasks()
        self.assertEqual(len(tasks), 100)
        for task in tasks.values():
            self.assertEqual(set(task), {"protocol", "pilot_id", "split", "prefix_text", "explanation", "sentences", "annotation_guide", "subtypes"})
            for span in task["sentences"]:
                self.assertEqual(span["text"], task["explanation"][span["start"]:span["end"]])


if __name__ == "__main__": unittest.main()
