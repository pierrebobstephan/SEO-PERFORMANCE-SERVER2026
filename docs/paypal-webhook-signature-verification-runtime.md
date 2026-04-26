# PayPal Webhook Signature Verification Runtime

## Ziel

Die Signaturpruefung wird lokal implementiert, aber bleibt bis zur echten Aktivierung operator- und server-governed.

## Inputs

- `PAYPAL_BUSINESS_CLIENT_ID`
- `PAYPAL_BUSINESS_CLIENT_SECRET`
- `PAYPAL_BUSINESS_WEBHOOK_ID`
- PayPal transmission headers
- Webhook-Event-Body

## Flow

1. OAuth-Token serverseitig gegen PayPal abrufen
2. `verify-webhook-signature` mit Webhook-ID und Event aufrufen
3. nur `SUCCESS` akzeptieren
4. alle anderen Faelle fail-closed behandeln

## Runtime-State

- implemented: ja
- live activated: nein
- approval required: ja
