# PayPal Webhook Separation Rule

## Grundsatz

Oeffentliche Marketing-, Buy-, Terms-, Support- oder Legal-Seiten duerfen niemals als PayPal-Webhook-Empfaenger dienen.

## Warum

- sie sind fuer Menschen und Crawler gedacht, nicht fuer signierte Server-Events
- sie vermischen Commerce-UI mit geschuetzter Billing-Infrastruktur
- sie verletzen die Doktrin `fail closed`, Scope-Trennung und minimale Angriffsoberflaeche

## Erlaubtes Modell

- PayPal-Events nur auf einem geschuetzten Receiver-Pfad
- serverseitige Signaturpruefung mit `PAYPAL_BUSINESS_WEBHOOK_ID`
- Replay-Schutz mit Transmission-ID-, Timestamp- und Nonce-Fenster
- event routing nur in protected, operator- oder server-governed Pfade

## Verbotene Beispiele

- `/buy`
- `/terms`
- `/support`
- jede andere Public-Portal-Seite
