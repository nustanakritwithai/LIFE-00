# LIFE-00 — LIFE-01 post-recovery acceptance contract V0.1

**Role:** LIFE-00 (ราชินีผู้สร้าง) is an **observer**. This document does not authorize changing LIFE-01's journal, ChatGPT Task, repository, or privileges.

**Target:** Verify the first LIFE-01 scheduled tick following restoration. The currently advertised slot is **2026-10-09 01:30 Asia/Bangkok**, with expected prior checkpoint CP003. Re-read the actual canonical journal first and adjust expectations if the records have legitimately advanced.

## Evidence hierarchy

1. Read the **current LIFE-01 canonical Google Doc** independently via an authorized connector; do not copy the whole private journal into public GitHub.
2. Read the **Scheduled Task metadata** independently. Verify `Enabled`, `XX:30 Asia/Bangkok`, and last-run timing if available. Some task views can return null even though another view shows a last run: record this as an evidence mismatch, **not a task failure**.
3. Verify `EVENT_ID: E004` and `CHECKPOINT_ID: CP004` occur **exactly once**; confirm `prior_CP: CP003`, `last_event: E004`, `prior_checkpoint: CP003`, `cycle: 4`, matching `tick_key=2026-10-09T01:30+07:00`, and `TRIGGER=CHATGPT_SCHEDULED_TASK`.
4. Verify the writes were **read back** from the canonical Doc. Confirm no competing writer or duplicated tick. If timestamps are ambiguous, state UNKNOWN.

## Decision table

| Evidence | Classification |
| --- | --- |
| Time has not reached 01:30 | WAITING_FOR_SCHEDULED_TICK |
| Task enabled, no new canonical pair yet | NO_CANONICAL_PAIR_YET; execution UNKNOWN |
| Only Event or only Checkpoint recorded | NEEDS_RECONCILIATION — DO NOT RETRY BLINDLY |
| Pair is duplicated or tick/prior links disagree | NEEDS_RECONCILIATION |
| Valid pair, read back; separate task-run metadata absent | PERSISTENCE_VERIFIED / SCHEDULED_TRIGGER_UNKNOWN |
| Valid pair, read back and task run independently verified | POST_RECOVERY_TICK_VERIFIED |
| Child reports an API error without trace | ERROR_USER_REPORTED; platform root cause UNKNOWN |
| No before/after benchmark | SKILL_GROWTH=UNKNOWN |

**No write of LIFE-01 E###/CP### by LIFE-00.** Never backfill missed slots. The observed first successful tick only tests one transition, not seven-day resilience or intelligence increase.

## Offline gate

`scripts/recovery_gate.py` accepts **sanitized, nonprivate evidence JSON** provided by an operator. It checks structural acceptance conditions; it **does not fetch Google Drive, read task logs, or authenticate its input**. Never cite its success as independent proof. See `tests/test_recovery_gate.py` for hypothetical cases. No secrets or canonical raw event logs may be committed.

## Seven-day continuity

Maintain a **private** per-day record: scheduled slots observed, run evidence, canonical pairs, readback outcome, duplicates/conflicts, errors, and independently measured benchmark changes. Publish only explicitly reviewed aggregates; UNKNOWN ≠ PASS.

## Deployment boundaries

The public Queen Dashboard remains a **template**, and the five-minute Typhoon pulse is **not configured**. GitHub Pages and future live-public exports require separate approval and verification.
