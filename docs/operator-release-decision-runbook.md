# Operator Release Decision Runbook

## Ziel

Dieses Runbook beschreibt den letzten lokalen Operator-Go/No-Go-Schritt vor einer spaeteren echten Kundenfreigabe.

## Schritte

1. Payment-Confirmation und Invoice-Confirmation auf Konsistenz pruefen.
2. Customer-Release-Authorization gegen Domain, Plan und Scope pruefen.
3. Support-Handover und Rollback-Readiness pruefen.
4. Protected Customer Release Decision lokal dokumentieren.
5. Reale Freigabe weiter `approval_required` halten, bis externe Systeme und Verantwortungen bestaetigt sind.

## Grenzen

- keine externe Freigabe aus dem Workspace
- keine offene Delivery
- keine Scope-Ausweitung
