# Production Cutover Gap Register

## Zweck

Dieses Register beschreibt den aktuellen, messbaren Abstand zwischen lokal kontrollierter Produktreife und realem Go-Live.

## Aktueller Ist-Stand

- Lizenz-, Domain-, Scope- und Rollback-Modelle sind lokal implementiert und testbar.
- Das Plugin faellt bei Domain-Mismatch, Konflikten, unklaren Freigaben oder unklarer Source-Mapping-Lage kontrolliert auf `observe_only`, `safe_mode` oder `approval_required` zurueck.
- Protected Delivery, Billing-Prep, Webhook-Prep, Signed-Delivery-Prep und Customer-Visibility sind lokal modelliert.
- Der geschuetzte PayPal-Webhook-Receiver ist lokal implementiert, aber nicht extern aktiviert.

## Bereits lokal geschlossen

- exakte `bound_domain`-Bindung pro Lizenz
- keine Wildcard-Bindings und keine Mehrprojekt-Uebertragung im Lizenzmodell
- Release-Kanaele `stable`, `pilot`, `rollback`
- Policy- und Rollback-Profile pro Domain
- Plugin-Fallback-Logik fuer Lizenz-, Domain-, Scope-, Policy-, Validation- und Rollback-Lage
- protected customer install pack
- payment, invoice, release decision, renewal und failed-payment Lebenszyklus als Operator-Pfad
- buyer-readable Admin-Sichten fuer Lizenz, Scope, Health, Delivery und Cutover
- lokale Build-, Test-, Packaging- und Artefaktpruefung

## Noch offene externe Go-Live-Gates

- echter Referenzpilot mit bestandenem Minimal-Scope, Validierung und Rollback-Drill
- reale PayPal-Secrets im Zielkontext:
  - `PAYPAL_BUSINESS_CLIENT_ID`
  - `PAYPAL_BUSINESS_CLIENT_SECRET`
  - `PAYPAL_BUSINESS_WEBHOOK_ID`
- reale Aktivierung des geschuetzten PayPal-Webhook-Receivers
- reale Signing-Key-Kette oder freigegebener Signing-Service
- reale protected delivery Infrastruktur auf Hetzner
- reale Checkout-, Payment-, Invoice- und Release-Freigabe ausserhalb des Workspace
- finaler Support-, Eskalations- und Incident-Prozess

## Noch offene interne Produktisierungs-Gates

- Referenzpilot-Runtime-Snapshot sauber schliessen
- Source-Mapping-Eindeutigkeit fuer erste reversible Produktionsstufe beweisen
- echte Before-State-, Primary-Metric-, Neighbor-Signal- und Post-Observation-Evidenz aus Referenzpilot sichern
- finale Four-Eyes- oder Operator-Freigabelogik fuer Release und Rollback schliessen

## Gate-Aussage

- lokaler Produktstand: `blueprint_ready_with_enforced_runtime_guardrails`
- externer produktiver Cutover: `approval_required`
