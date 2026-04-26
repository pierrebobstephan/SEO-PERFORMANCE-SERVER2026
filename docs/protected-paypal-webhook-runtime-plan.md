# Protected PayPal Webhook Runtime Plan

## Ziel

Der PayPal-Webhook-Empfaenger wird als geschuetzter, serverseitiger Runtime-Pfad implementiert, ohne den Public-Portal-Scope zu erweitern.

## Runtime Path

- path: `/protected/paypal/webhook`
- bind scope: geschuetzter Suite-Receiver, nicht Public-Portal
- accepted methods: `POST`
- doctrine state: `approval_required`
- billing scope: `paypal_billing_events_only`

## Fail-Closed-Regeln

- fehlende Env-Refs -> blockieren
- ungueltige Signatur -> blockieren
- Replay-Verdacht -> blockieren
- malformed payload -> blockieren
- unsupported event scope -> blockieren

## Routing

- keine Customer-Ausfuehrung
- kein Public-Fulfillment
- nur protected operator/server-governed routing
