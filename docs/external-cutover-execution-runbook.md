# External Cutover Execution Runbook

## Ziel

Dieses Runbook macht den letzten externen Cutover-Pfad fuer PayPal, den geschuetzten Webhook-Receiver, Signing, Delivery und den finalen Go/No-Go-Schritt konkret.

## Scope

- exact licensed domain: `wp.electri-c-ity-studios-24-7.com`
- public base URL: `https://site-optimizer.electri-c-ity-studios-24-7.com`
- protected PayPal webhook URL: `https://site-optimizer.electri-c-ity-studios-24-7.com/protected/paypal/webhook`
- doctrine state bleibt bis zur echten Freigabe: `approval_required`

## Reihenfolge

1. Lokale Preconditions pruefen.
   - `final-global-productization-readiness.json` muss fuer die Commercial Chain `locally_verified_waiting_external_inputs` zeigen.
   - `final-real-staging-paypal-webhook-prep.json` muss fuer `local_runtime_verification.state` auf `passed` stehen.
2. PayPal-Env-Refs im Zielsystem injizieren.
   - `PAYPAL_BUSINESS_CLIENT_ID`
   - `PAYPAL_BUSINESS_CLIENT_SECRET`
   - `PAYPAL_BUSINESS_WEBHOOK_ID`
   - Keine Klartext-Secrets im Repo.
3. Protected Receiver im Zielsystem binden und neu laden.
   - Route bleibt `/protected/paypal/webhook`.
   - Keine oeffentliche Portal-Route darf diese Funktion uebernehmen.
4. Reale Staging-Webhooks pruefen.
   - Signatur muss mit realem `PAYPAL_BUSINESS_WEBHOOK_ID` verifiziert werden.
   - Replay-Schutz muss Duplikate blockieren.
   - Evidence-Log und Nonce-Registry muessen im Zielsystem geschrieben werden.
5. Signing- und Delivery-Ziel pruefen.
   - echte Signing-Referenz hinter `local_server_signing_key`
   - geschuetztes Delivery-Ziel und Grant-Regel bestaetigt
6. Menschliche Verantwortungen schliessen.
   - Support-Eskalation
   - Billing-/Invoice-Verantwortung
   - Release-Authority
   - Rollback-Owner
7. Finales Go/No-Go dokumentieren.
   - Nur wenn alle blocking items der External Cutover Checklist auf `verified_in_target` oder ein explizit freigegebenes Aequivalent stehen.

## Abort-Kriterien

- fehlende Env-Refs nach Zielsystem-Deployment
- Signaturverifikation scheitert im realen Staging
- Replay-Schutz blockiert Duplikate nicht
- Signing- oder Delivery-Ziel bleibt unklar
- Support-, Billing- oder Release-Owner fehlen

## Rollback

- Webhook-Aktivierung zuruecknehmen
- geschuetzte Delivery deaktivieren
- Signing-Referenz entkoppeln
- Customer Release auf `approval_required` halten
- vorige Package-/Policy-Stufe ueber den Rollback-Kanal aktiv halten

## Referenzen

- [External Inputs Required For Real Cutover](/opt/electri-city-ops/docs/external-inputs-required-for-real-cutover.md)
- [Protected PayPal Webhook Runtime Plan](/opt/electri-city-ops/docs/protected-paypal-webhook-runtime-plan.md)
- [PayPal Webhook Verification Flow](/opt/electri-city-ops/docs/paypal-webhook-verification-flow.md)
- [Secret And Certificate Handling Plan](/opt/electri-city-ops/docs/secret-and-certificate-handling-plan.md)
- [Operator Release Decision Runbook](/opt/electri-city-ops/docs/operator-release-decision-runbook.md)

## Status

- Execution Runbook: `implemented_locally`
- echte externe Ausfuehrung: `approval_required`
