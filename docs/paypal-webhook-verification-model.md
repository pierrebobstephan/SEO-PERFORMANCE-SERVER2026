# PayPal Webhook Verification Model

## Ziel

Webhook-Verifikation wird technisch vorbereitet, ohne eine oeffentliche Route oder offene Billing-Schnittstelle freizugeben.

## Modell

- Protected receiver candidate:
  - `https://site-optimizer.electri-c-ity-studios-24-7.com/protected/paypal/webhook`
- Verifikations-Endpoint:
  - `https://api-m.paypal.com/v1/notifications/verify-webhook-signature`
- Webhook-ID nur als Env-Referenz
- Event-Routing:
  - `protected_operator_console_only`
- Replay-Schutz:
  - `transmission_id_time_window_and_nonce_registry`
- Public Exposure:
  - `false`

## Konsequenz

Solange keine reale, freigegebene Delivery- und Billing-Infrastruktur steht, bleibt der Webhook-Pfad:

- lokal modelliert
- approval-gated
- nicht oeffentlich
