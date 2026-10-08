"""Offline structural gate for a sanitized LIFE-01 recovery evidence bundle.

This does NOT fetch canonical Google Drive data, verify signatures or access ChatGPT
task history. Outputs are conditional on supplied inputs and NOT a live audit.
"""
from datetime import datetime, timedelta
import json
import sys

TARGET_TICK = "2026-10-09T01:30+07:00"
TARGET_EVENT = "E004"
TARGET_CHECKPOINT = "CP004"
PRIOR_CHECKPOINT = "CP003"
EXPECTED_CYCLE = 4


def _time(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else None
    except (AttributeError, ValueError):
        return None


def _result(status, **kwargs):
    return {
        "status": status,
        "proof": "OFFLINE_INPUT_ONLY_NOT_INDEPENDENT_EVIDENCE",
        **kwargs,
    }


def evaluate(bundle):
    """Check expected ID uniqueness and linkage; refuse to invent a PASS."""
    if not isinstance(bundle, dict):
        return _result("INVALID_EVIDENCE")
    now, tick = _time(bundle.get("observed_at")), _time(TARGET_TICK)
    if now is None:
        return _result("INVALID_OBSERVATION_TIME")
    if now < tick:
        return _result("WAITING_FOR_SCHEDULED_TICK")

    task = bundle.get("task")
    if not isinstance(task, dict) or task.get("enabled") is not True:
        return _result("TASK_DISABLED_OR_UNKNOWN")
    if task.get("schedule") != "HOURLY_XX30_ASIA_BANGKOK":
        return _result("SCHEDULE_MISMATCH")

    events, checkpoints = bundle.get("events"), bundle.get("checkpoints")
    if not isinstance(events, list) or not isinstance(checkpoints, list):
        return _result("EVIDENCE_RECORDS_UNAVAILABLE")
    if not all(isinstance(x, dict) for x in events + checkpoints):
        return _result("INVALID_EVIDENCE")
    # Reject duplicated IDs anywhere in the supplied event/checkpoint inventory.
    eids = [x.get("event_id") for x in events]
    cids = [x.get("checkpoint_id") for x in checkpoints]
    if len(eids) != len(set(eids)) or len(cids) != len(set(cids)):
        return _result("NEEDS_RECONCILIATION", reason="DUPLICATE_IDS")

    matching_events = [x for x in events if x.get("event_id") == TARGET_EVENT]
    matching_cps = [x for x in checkpoints if x.get("checkpoint_id") == TARGET_CHECKPOINT]
    if not matching_events and not matching_cps:
        return _result("NO_CANONICAL_PAIR_YET", task_run="UNKNOWN")
    if len(matching_events) != 1 or len(matching_cps) != 1:
        return _result("NEEDS_RECONCILIATION", reason="PARTIAL_PAIR")

    event, cp = matching_events[0], matching_cps[0]
    if not (
        event.get("prior_cp") == PRIOR_CHECKPOINT
        and cp.get("prior_checkpoint") == PRIOR_CHECKPOINT
        and cp.get("last_event") == TARGET_EVENT
        and cp.get("cycle") == EXPECTED_CYCLE
        and event.get("tick_key") == TARGET_TICK
        and cp.get("tick_key") == TARGET_TICK
        and event.get("trigger") == "CHATGPT_SCHEDULED_TASK"
    ):
        return _result("NEEDS_RECONCILIATION", reason="LINKAGE_OR_TICK_CONFLICT")

    if bundle.get("readback_confirmed") is not True:
        return _result("READBACK_UNVERIFIED")

    last_run = _time(task.get("last_run_time"))
    if last_run is None or not (tick <= last_run < tick + timedelta(hours=1)):
        return _result("PERSISTENCE_INDICATED_RUN_METADATA_UNKNOWN")

    return _result("GATE_PASSED_ON_SUPPLIED_EVIDENCE")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/recovery_gate.py <sanitized-evidence.json>", file=sys.stderr)
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            value = json.load(f)
    except (OSError, ValueError) as exc:
        print("Could not load evidence: " + str(exc), file=sys.stderr)
        return 2
    result = evaluate(value)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "GATE_PASSED_ON_SUPPLIED_EVIDENCE" else 1


if __name__ == "__main__":
    sys.exit(main())
