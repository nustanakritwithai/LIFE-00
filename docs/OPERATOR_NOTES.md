# LIFE-00 / Creator Queen Console — operating contract

## Agent boundary

- LIFE-00 is an observer/controller role, not a conscious being.
- LIFE-01 runs in its own chat, repository and private journal.
- Never copy raw or personally identifying LIFE-01 memories into this public repo.
- UNKNOWN ≠ PASS. Checkpoints and skill claims need evidence, not narrative.

## Clock (Asia/Bangkok)

| System | Intended cadence | Ownership |
| --- | --- | --- |
| LIFE-00 ChatGPT audit | hourly at minute 00 | LIFE-00 |
| LIFE-01 ChatGPT episode | hourly at minute 30 | LIFE-01 |
| LIFE-01 basic pulse | every 5 minutes | planned GitHub Actions in Life-01 repo |

A scheduled trigger is not proof of successful execution. Do not count missed pulses as experiences. GitHub Actions may start late or miss runs; pulse log IDs must be idempotent.

## Public dashboard

`docs/index.html` renders `docs/status.json` **as an explicit template**.
`snapshot_kind=TEMPLATE_ONLY`, `public_data_approved=false`, and `dashboard_status=NOT_DEPLOYED` are deliberate.

There is no automatic Drive-to-Pages bridge. Future releases may import only approved, sanitized JSON with independent review and no private identifiers.

## Deployment gate

1. Review PR and run tests.
2. Owner explicitly approves content and publishing.
3. Confirm Pages source/deployment choice with current GitHub settings.
4. Merge/deploy only after approval and verify public URL externally.

Do not place tokens or Google Drive credentials in Git history.
