# External Inputs Required For Real Cutover

Die lokale Suite kann die letzten externen Schritte nicht erfinden. Vor einem echten globalen Cutover werden diese Inputs real gebraucht:

Maschinenlesbare Referenz:

- `config/external-cutover-checklist.json`
- `manifests/previews/final-external-cutover-package.json`

## PayPal Business

- `PAYPAL_BUSINESS_CLIENT_ID`
- `PAYPAL_BUSINESS_CLIENT_SECRET`
- `PAYPAL_BUSINESS_WEBHOOK_ID`
- verifizierter und real aktivierter geschuetzter PayPal-Webhook-Receiver

## Reference Pilot

- echter Runtime-Snapshot der installierten Bridge
- bestaetigter Referenzpilot-Entscheid

## Signing And Delivery

- echte lokale oder externe Signaturausfuehrung hinter `local_server_signing_key`
- operative Replay-Protection-Durchsetzung im realen Cutover
- geschuetzte Delivery-Infrastruktur muss real bereitstehen, auch wenn Ziel und Grant-Regel bereits modelliert sind

## Optional But Operationally Helpful

- finaler Eskalationspfad hinter der Support-E-Mail
- reale Rechnungsfreigabe-Person, falls automatische Zahlungs- und Invoice-Reconciliation `inconclusive` bleibt
