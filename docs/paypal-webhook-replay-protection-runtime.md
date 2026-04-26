# PayPal Webhook Replay Protection Runtime

## Ziel

Replay-Verdacht wird lokal mit engem Scope und fail-closed Verhalten behandelt.

## Mechanik

- `PAYPAL-TRANSMISSION-ID`
- `PAYPAL-TRANSMISSION-TIME`
- Event-ID
- lokales Nonce-/Event-Registry im Workspace

## Regeln

- Timestamp ausserhalb des erlaubten Fensters -> `replay_suspected`
- bereits bekannte Kombination aus Transmission-ID und Event-ID -> `replay_suspected`
- fehlende Replay-Inputs -> `malformed_event`

## Persistenz

- evidence log: `var/state/json/paypal_webhook_evidence.jsonl`
- nonce registry: `var/state/json/paypal_webhook_nonce_registry.json`
