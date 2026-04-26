# Post Install Guardrail Sequence

## Guardrails

- domain bound only
- staging only
- safe_mode / observe_only first
- no ownership takeover while source mapping is unclear
- rollback path must stay intact
- no global site rewrite

## Gate

- Post Install Guardrail Sequence: `approval_required`
