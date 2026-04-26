# PayPal Webhook Event Routing Model

## Scope

Nur Billing-Ereignisse werden akzeptiert.

## Accepted Routing

- `protected_operator_server_governed`

## Nicht erlaubt

- Customer-facing execution
- Public fulfillment
- Buy-page execution
- offene Billing-API

## Resultat

Ein akzeptiertes Event erzeugt nur geschuetzte lokale Evidenz und bleibt bis zur weiteren Operator-/Server-Freigabe `approval_required`.
