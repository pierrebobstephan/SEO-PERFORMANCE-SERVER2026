# PayPal Webhook Verification Flow

## Ziel

Webhook-Verifikation bleibt geschuetzt, serverseitig und billing-spezifisch.

## Flow

1. PayPal sendet Event an den geschuetzten Receiver:
   - `https://site-optimizer.electri-c-ity-studios-24-7.com/protected/paypal/webhook`
2. Server liest `PAYPAL_BUSINESS_WEBHOOK_ID` als Env-Ref.
3. Server validiert Signatur gegen:
   - `https://api-m.paypal.com/v1/notifications/verify-webhook-signature`
4. Server prueft Replay-Schutz:
   - Transmission-ID
   - Timestamp-Fenster
   - dedizierte Nonce-/Event-Registry
5. Erst danach darf das Event in protected operator/server-governed Billing-Logik einfliessen.

## Status im Workspace

- lokal modelliert
- produktionsnah vorbereitet
- lokaler Signatur- und Replay-Selbsttest ist implementiert
- nicht live exponiert
- reale Aktivierung bleibt `approval_required`
