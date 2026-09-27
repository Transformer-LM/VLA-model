"""Behavioral regression tests using temporary projects, no models or GPUs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
from evidence_contract import fingerprints
from diagnose_run import diagnose
from validate_project import resolve_skill, PHASE_SKILLS


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = json.loads((SKILL / "assets/AUTORESEARCH_CONFIG.template.json").read_text())
        self.config["research"].update(exploration_level="direction", direction="test")
        self.config["compute"].update(max_total_gpu_hours=2, max_parallel_jobs=2)
        self.write("AUTORESEARCH_CONFIG.json", self.config)
        self.cli("init", "--run-id", "test-run", "--direction", "test")

    def write(self, name, value="evidence"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if isinstance(value, (dict, list)) else value, encoding="utf-8")
        return name

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SKILL / "scripts/research_state.py"),
                                 "--root", str(self.root), *args], capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def state(self):
        return json.loads(self.cli("status", "--json").stdout)

    def phase(self, name, paths):
        self.cli("begin", name)
        for path in paths:
            if not (self.root / path).exists():
                self.write(path)
        self.cli("complete", name, "--gate", "pass", "--acceptance", "provisional")

    def prepare_execution(self):
        self.phase("contract", ["research-stage/WAM_ROUTE_CARD.md"])
        self.phase("evidence-map", ["research-stage/LITERATURE_MAP.md"])
        self.write("idea-stage/NOVELTY_REPORT.json", {
            "search_status": "complete", "novelty_status": "potentially_distinct",
            "evidence_coverage": "sufficient_for_current_claim",
            "verified_prior_work": [{"id": "example", "url": "https://example.org", "evidence": "section 3"}],
            "delta": "test intervention"})
        self.phase("idea-discovery", ["idea-stage/IDEA_REPORT.md", "idea-stage/WAM_ROUTE_CARDS.md"])
        self.write("evaluation/eval.py", "success = True\n")
        self.protocol = {"protocol_id": "p1", "primary_metric": "success",
            "budget_basis": "gpu_hours", "checkpoint_selection": "development_only",
            "aggregation_unit": "training_run", "uncertainty_method": "paired",
            "stopping_rule": "fixed sample", "editable_paths": ["policy/"],
            "protected_files": fingerprints(self.root, ["evaluation/eval.py"])}
        self.write("refine-logs/EXPERIMENT_PROTOCOL.json", self.protocol)
        self.phase("method-plan", ["refine-logs/FINAL_PROPOSAL.md", "refine-logs/EXPERIMENT_PLAN.md",
                                   "refine-logs/PREFLIGHT_REPORT.md"])
        self.cli("begin", "implementation-experiments")

    def experiment(self, outcome="inconclusive"):
        self.prepare_execution()
        self.cli("reserve-job", "job1", "--gpu-hours", "1")
        self.cli("reconcile-job", "job1", "--gpu-hours", "0.5", "--outcome", "completed")
        artifacts = {"config": self.write("runs/E1/config.json", {"seed": 0}),
                     "log": self.write("runs/E1/stdout.txt", "finished"),
                     "source_snapshot": self.write("runs/E1/source.txt", "source revision"),
                     "metrics": self.write("runs/E1/metrics.json", {"success": 0.4, "unrelated": 0.9})}
        self.manifest = {"experiment_id": "E1", "parent_id": None, "hypothesis_id": "H1",
            "job_id": "job1", "protocol_id": "p1", "operation": "baseline",
            "execution_status": "completed", "scientific_outcome": outcome,
            "condition_id": "baseline", "training_seed": 0, "artifacts": artifacts}
        self.write("runs/E1/manifest.json", self.manifest)
        self.cli("record-experiment", "--manifest", "runs/E1/manifest.json")
        self.write("refine-logs/EXPERIMENT_TRACKER.md")
        self.write("refine-logs/EXPERIMENT_RESULTS.md")
        self.cli("complete", "implementation-experiments", "--gate", "pass", "--acceptance", "provisional")

    def audit(self, outcome="inconclusive", finish=True):
        self.experiment(outcome)
        self.cli("begin", "evidence-audit")
        state = self.state()
        inputs = ["runs/E1/manifest.json", *self.manifest["artifacts"].values()]
        self.write("refine-logs/ANALYSIS_REPORT.md")
        self.write("refine-logs/EXPERIMENT_AUDIT.json", {
            "run_id": "test-run", "revision": state["phases"]["evidence-audit"]["revision"],
            "integrity": "pass", "input_hashes": fingerprints(self.root, inputs)})
        self.verdict = {"run_id": "test-run", "revision": 1,
            "input_hashes": fingerprints(self.root, ["refine-logs/EXPERIMENT_AUDIT.json", "runs/E1/metrics.json"]),
            "claims": [{"id": "C1", "statement": "scoped result", "status": outcome,
                        "scope": "pilot", "experiment_ids": ["E1"],
                        "metrics": [{"source": "runs/E1/metrics.json", "key_path": ["success"], "value": 0.4}]}]}
        self.write("refine-logs/CLAIM_VERDICT.json", self.verdict)
        if finish:
            self.cli("adjudicate", "evidence-audit", "--acceptance", "provisional")

    def test_complete_negative_dossier(self):
        self.audit("refuted")
        self.cli("begin", "review-improvement")
        self.write("review-stage/AUTO_REVIEW.md")
        self.write("review-stage/REVIEW_STATE.json", {"run_id": "test-run", "revision": 1,
            "reviewer": "test reviewer", "model": "test model", "unresolved_critical": [],
            "input_hashes": fingerprints(self.root, ["refine-logs/EXPERIMENT_AUDIT.json", "refine-logs/CLAIM_VERDICT.json"])})
        self.cli("adjudicate", "review-improvement", "--acceptance", "provisional")
        self.phase("research-synthesis", ["research-stage/RESEARCH_DOSSIER.md", "AUTORESEARCH_STATUS.md"])
        self.assertEqual(self.state()["overall_status"], "completed")
        self.assertEqual(self.state()["overall_assurance"], "provisional")

    def test_arbitrary_nonempty_file_cannot_complete(self):
        self.cli("begin", "contract")
        self.write("unrelated.txt")
        self.cli("complete", "contract", "--gate", "pass", "--acceptance", "deterministic",
                 "--artifact", "unrelated.txt", ok=False)

    def test_empty_search_is_not_novelty(self):
        self.phase("contract", ["research-stage/WAM_ROUTE_CARD.md"])
        self.phase("evidence-map", ["research-stage/LITERATURE_MAP.md"])
        self.write("idea-stage/IDEA_REPORT.md")
        self.write("idea-stage/WAM_ROUTE_CARDS.md")
        self.write("idea-stage/NOVELTY_REPORT.json", {"search_status": "failed", "novelty_status": "potentially_distinct"})
        self.cli("begin", "idea-discovery")
        self.cli("complete", "idea-discovery", "--gate", "pass", "--acceptance", "provisional", ok=False)

    def test_frozen_evaluator_change_invalidates_plan(self):
        self.prepare_execution()
        self.write("evaluation/eval.py", "changed success rule")
        state = self.state()
        self.assertEqual(state["phases"]["method-plan"]["status"], "pending")
        self.assertEqual(state["phases"]["method-plan"]["revision"], 2)
        self.cli("reserve-job", "job1", "--gpu-hours", "1", ok=False)

    def test_raw_metric_change_invalidates_audit(self):
        self.audit()
        self.write("runs/E1/metrics.json", {"success": 0.99})
        state = self.state()
        self.assertEqual(state["phases"]["evidence-audit"]["status"], "pending")
        self.assertTrue(state["experiments"]["E1"]["stale"])

    def test_generic_complete_cannot_adjudicate(self):
        self.audit(finish=False)
        self.cli("complete", "evidence-audit", "--gate", "pass", "--acceptance", "provisional", ok=False)

    def test_unrelated_number_cannot_verify_metric(self):
        self.audit(finish=False)
        self.verdict["claims"][0]["metrics"][0]["value"] = 0.9
        self.write("refine-logs/CLAIM_VERDICT.json", self.verdict)
        self.cli("adjudicate", "evidence-audit", "--acceptance", "provisional", ok=False)

    def test_wrong_revision_rejected(self):
        self.audit(finish=False)
        self.verdict["revision"] = 0
        self.write("refine-logs/CLAIM_VERDICT.json", self.verdict)
        self.cli("adjudicate", "evidence-audit", "--acceptance", "provisional", ok=False)

    def test_unproven_independent_review_rejected(self):
        self.audit(finish=False)
        self.cli("adjudicate", "evidence-audit", "--acceptance", "independent", ok=False)

    def test_single_seed_cannot_promote_main_claim(self):
        self.audit(finish=False)
        self.verdict["claims"][0].update(scope="main", status="supported")
        self.write("refine-logs/CLAIM_VERDICT.json", self.verdict)
        self.cli("adjudicate", "evidence-audit", "--acceptance", "provisional", ok=False)

    def test_original_raw_evidence_can_be_restored(self):
        self.audit()
        self.write("runs/E1/metrics.json", {"success": 0.99})
        self.state()
        self.write("runs/E1/metrics.json", {"success": 0.4, "unrelated": 0.9})
        self.assertNotIn("stale", self.state()["experiments"]["E1"])

    def test_legacy_completed_state_reopens_without_losing_files(self):
        self.phase("contract", ["research-stage/WAM_ROUTE_CARD.md"])
        path = self.root / ".aris/autoresearch/runs/test-run/state.json"
        state = json.loads(path.read_text())
        del state["phases"]["contract"]["artifact_hashes"]
        path.write_text(json.dumps(state))
        self.assertEqual(self.state()["phases"]["contract"]["status"], "pending")
        self.assertTrue((self.root / "research-stage/WAM_ROUTE_CARD.md").is_file())

    def test_reservations_include_running_jobs(self):
        self.prepare_execution()
        self.cli("reserve-job", "job1", "--gpu-hours", "1.5")
        self.cli("reserve-job", "job2", "--gpu-hours", "1", ok=False)
        self.assertEqual(len(self.state()["jobs"]), 1)

    def test_settlement_is_idempotent(self):
        self.prepare_execution()
        self.cli("reserve-job", "job1", "--gpu-hours", "1")
        for _ in range(2):
            self.cli("reconcile-job", "job1", "--gpu-hours", "0.5", "--outcome", "failed")
        self.assertEqual(self.state()["usage"]["gpu_hours"], 0.5)
        self.cli("reconcile-job", "job1", "--gpu-hours", "0.4", "--outcome", "failed", ok=False)

    def test_overrun_recorded_and_blocks_next_job(self):
        self.prepare_execution()
        self.cli("reserve-job", "job1", "--gpu-hours", "1")
        self.cli("reconcile-job", "job1", "--gpu-hours", "3", "--outcome", "failed")
        self.assertEqual(self.state()["overall_status"], "blocked")
        self.cli("reserve-job", "job2", "--gpu-hours", "0.1", ok=False)

    def test_nan_usage_rejected(self):
        self.prepare_execution()
        self.cli("reserve-job", "job1", "--gpu-hours", "nan", ok=False)
        self.assertEqual(self.state()["jobs"], {})

    def test_reopen_archives_downstream(self):
        self.audit()
        self.cli("reopen", "implementation-experiments", "--reason", "additional ablation")
        state = self.state()
        self.assertEqual(state["phases"]["evidence-audit"]["status"], "pending")
        self.assertTrue(state["phases"]["evidence-audit"]["revisions"])
        self.assertEqual(state["usage"]["gpu_hours"], 0.5)

    def test_active_reservation_blocks_reopen(self):
        self.prepare_execution()
        self.cli("reserve-job", "job1", "--gpu-hours", "1")
        self.cli("reopen", "method-plan", "--reason", "change", ok=False)

    def test_diagnosis_does_not_reject_hypothesis(self):
        self.experiment()
        result = diagnose(self.root, ["runs/E1/manifest.json"])
        self.assertEqual(result["scientific_verdict"], "not_adjudicated")
        self.assertIn("inconclusive", {f["type"] for f in result["findings"]})
        self.assertIn("insufficient_seeds", {f["type"] for f in result["findings"]})

    def test_skill_resolution_does_not_require_future_reviewer(self):
        self.write("skills/all-local-skills/paper-search/SKILL.md")
        self.assertIsNotNone(resolve_skill(self.root, "paper-search", self.config))
        self.assertNotIn("auto-review-loop", PHASE_SKILLS["evidence-map"])


if __name__ == "__main__":
    unittest.main()
