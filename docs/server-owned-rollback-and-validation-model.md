# Server-Owned Rollback And Validation Model

## Ziel

Rollback und Validation werden fuer den spaeteren Realbetrieb serverseitig ueber die Bridge getragen, nicht ueber manuelle Kundeneingriffe.

## Bindung

- `rollback_owner = server_managed_bridge`
- `validation_owner = server_managed_bridge`

## Bedeutung

- Der Kunde sieht den Status im Plugin.
- Die operative Verantwortung fuer Guardrails, Validation und Rollback bleibt auf der geschuetzten Suite-Seite.
- Reversible Eingriffe duerfen erst erfolgen, wenn diese serverseitige Verantwortung gruen und nachvollziehbar bleibt.

## Nicht-Ziele

- keine globale automatische Site-Reparatur
- keine unvalidierte Selbstmodifikation
- keine Scope-Ausweitung ueber die freigegebenen Pilotgrenzen hinaus
