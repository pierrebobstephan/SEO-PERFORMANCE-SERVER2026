# PayPal Business Integration Model

## Ziel

Der PayPal-Business-Pfad wird produktionsnah, aber weiterhin lokal und geschuetzt vorbereitet.

## Grenzen

- keine Klartext-Secrets im Repo
- keine offenen Public-Checkout- oder Invoice-Routen
- keine offene Webhook-API
- keine Kunden-Login-Schicht
- keine Live-PayPal-Aufrufe aus dem Workspace ohne ausdrueckliche Freigabe

## Konfiguration

- Datei: `config/paypal-business.json`
- Secret-Referenzen nur ueber:
  - `PAYPAL_BUSINESS_CLIENT_ID`
  - `PAYPAL_BUSINESS_CLIENT_SECRET`
  - `PAYPAL_BUSINESS_WEBHOOK_ID`
- Support-Kanal:
  - `pierre.stephan1@electri-c-ity-studios.com`

## Modellierte Endpunkte

- OAuth Token: `https://api-m.paypal.com/v1/oauth2/token`
- Order Capture: `https://api-m.paypal.com/v2/checkout/orders/{order_id}/capture`
- Invoice Create: `https://api-m.paypal.com/v2/invoicing/invoices`
- Invoice Send: `https://api-m.paypal.com/v2/invoicing/invoices/{invoice_id}/send`
- Webhook Verify: `https://api-m.paypal.com/v1/notifications/verify-webhook-signature`

## Server-Verantwortung

- `server_validation_owner = server_managed_bridge`
- `server_rollback_owner = server_managed_bridge`

Die Bridge darf erst dann ueber reine Vorbereitung hinausgehen, wenn Validierung, Rollback, Delivery und Billing-Gates gruen sind.
