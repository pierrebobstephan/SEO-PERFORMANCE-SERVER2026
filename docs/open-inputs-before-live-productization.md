# Open Inputs Before Live Productization

## Zweck

Dieses Dokument sammelt nur die Inputs, die fuer den echten Referenzpilot und den spaeteren externen Cutover noch verbindlich fehlen.

## Noch offene externe Inputs

- Referenzpilot-Freigabe fuer genau eine echte Ziel-Domain
- belastbarer Runtime-Snapshot der installierten Bridge auf dem Referenzsystem
- reale PayPal-Env-Refs im Zielkontext:
  - `PAYPAL_BUSINESS_CLIENT_ID`
  - `PAYPAL_BUSINESS_CLIENT_SECRET`
  - `PAYPAL_BUSINESS_WEBHOOK_ID`
- Aktivierungsfreigabe fuer den geschuetzten Webhook-Pfad
- Signing-Key- oder Signing-Service-Freigabe
- Delivery-Ziel und Delivery-Handover ausserhalb des Workspace

## Noch offene betriebliche Inputs

- finaler Support- und Eskalationsprozess
- Incident- und Rollback-Owner fuer echte Kundenfaelle
- Freigabeprozess fuer Payment-Confirmation, Invoice-Confirmation und Release Decision
- Nachbeobachtungsfenster und Metrikverantwortung fuer Referenzpilot und erste Live-Freigabe

## Noch offene Pilot-Inputs

- bestaetigte Before-State-Evidenz des Referenzsystems
- bestaetigte Primary Metrics
- bestaetigte Neighbor Signals
- bestaetigte Abort-Kriterien
- bestaetigte Rollback-Kriterien
- bestaetigte Post-Observation-Dauer

## Bereits lokal vorbereitet

- exact-domain Lizenzmodell
- protected customer fulfillment path
- signed delivery prep
- protected PayPal webhook runtime
- billing, invoice, release decision, renewal und failed-payment Modellierung
- buyer- und operator-readable status surfaces

## Status

- offene Inputs: `operator input required`
- externer Cutover: `approval_required`
