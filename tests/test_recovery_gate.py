"""Hypothetical cases for the offline post-recovery acceptance gate."""
import copy
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from recovery_gate import evaluate  # noqa: E402


def fixture():
    return {
        "observed_at": "2026-10-09T01:35:00+07:00",
        "task": {
            "enabled": True,
            "schedule": "HOURLY_XX30_ASIA_BANGKOK",
            "last_run_time": "2026-10-08T18:31:00Z",
        },
        "events": [{
            "event_id": "E004",
            "prior_cp": "CP003",
            "tick_key": "2026-10-09T01:30+07:00",
            "trigger": "CHATGPT_SCHEDULED_TASK",
        }],
        "checkpoints": [{
            "checkpoint_id": "CP004",
            "prior_checkpoint": "CP003",
            "last_event": "E004",
            "cycle": 4,
            "tick_key": "2026-10-09T01:30+07:00",
        }],
        "readback_confirmed": True,
    }


class RecoveryAcceptanceTests(unittest.TestCase):
    def assert_gate(self, f, expected):
        result = evaluate(f)
        self.assertEqual(result["status"], expected)
        self.assertEqual(result["proof"], "OFFLINE_INPUT_ONLY_NOT_INDEPENDENT_EVIDENCE")

    def test_conditional_pass_with_full_evidence(self):
        self.assert_gate(fixture(), "GATE_PASSED_ON_SUPPLIED_EVIDENCE")

    def test_before_tick(self):
        f = fixture()
        f["observed_at"] = "2026-10-09T01:20:00+07:00"
        self.assert_gate(f, "WAITING_FOR_SCHEDULED_TICK")

    def test_missing_pair(self):
        f = fixture()
        f["events"] = []
        f["checkpoints"] = []
        self.assert_gate(f, "NO_CANONICAL_PAIR_YET")

    def test_missing_checkpoint(self):
        f = fixture()
        f["checkpoints"] = []
        self.assert_gate(f, "NEEDS_RECONCILIATION")

    def test_duplicate_event(self):
        f = fixture()
        f["events"].append(copy.deepcopy(f["events"][0]))
        self.assert_gate(f, "NEEDS_RECONCILIATION")

    def test_wrong_tick_key(self):
        f = fixture()
        f["events"][0]["tick_key"] = "2026-10-08T20:30+07:00"
        self.assert_gate(f, "NEEDS_RECONCILIATION")

    def test_wrong_prior_checkpoint(self):
        f = fixture()
        f["checkpoints"][0]["prior_checkpoint"] = "CP002"
        self.assert_gate(f, "NEEDS_RECONCILIATION")

    def test_no_readback(self):
        f = fixture()
        f["readback_confirmed"] = False
        self.assert_gate(f, "READBACK_UNVERIFIED")

    def test_task_history_absent(self):
        f = fixture()
        f["task"]["last_run_time"] = None
        self.assert_gate(f, "PERSISTENCE_INDICATED_RUN_METADATA_UNKNOWN")

    def test_disabled_task(self):
        f = fixture()
        f["task"]["enabled"] = False
        self.assert_gate(f, "TASK_DISABLED_OR_UNKNOWN")

    def test_schedule_mismatch(self):
        f = fixture()
        f["task"]["schedule"] = "HOURLY_XX00_ASIA_BANGKOK"
        self.assert_gate(f, "SCHEDULE_MISMATCH")

    def test_invalid_input_does_not_pass(self):
        self.assert_gate({}, "INVALID_OBSERVATION_TIME")


if __name__ == "__main__":
    unittest.main()
