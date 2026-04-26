# PayPal Webhook Local Evidence Model

## Ziel

Jeder Webhook-Versuch wird nachvollziehbar, lokal und reversibel dokumentiert.

## Evidence Fields

- `received_at`
- `event_type`
- `verification_state`
- `replay_state`
- `routing_state`
- `doctrine_state`
- `receiver_runtime_state`

## Speicherort

- `var/state/json/paypal_webhook_evidence.jsonl`

## Zweck

- Auditierbarkeit
- Debugging
- Rollback-nahe Nachvollziehbarkeit
- keine Customer- oder Public-Sicht
