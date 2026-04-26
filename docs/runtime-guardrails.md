# Runtime Guardrails

## Zweck

Dieses Dokument beschreibt die lokale Laufzeitdurchsetzung der 8.0-Masterdoktrin.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Die Guardrails bevorzugen `observe_only`, `approval_required` und `blocked` vor jeder unklaren Wirkung.
2. Bleibt es innerhalb des Workspace?
   Ja. Die Laufzeitlogik arbeitet nur mit lokalen Daten, Policy-Dateien und Cycle-Artefakten.
3. Hat es irgendeine externe Wirkung?
   Nein. Es gibt keine Connector-Nutzung und keine Aktivierung externer Komponenten.
4. Braucht es Approval?
   Nein fuer die lokale Durchsetzung.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Rueckweg ist das lokale Zuruecknehmen der Doctrine-Enforcement-Integration.

## Technische Komponenten

- [doctrine.py](/opt/electri-city-ops/src/electri_city_ops/doctrine.py)
- [orchestrator.py](/opt/electri-city-ops/src/electri_city_ops/orchestrator.py)
- [cli.py](/opt/electri-city-ops/src/electri_city_ops/cli.py)

## Runtime-Checks

### Policy-Checks

- Policy-Datei laden oder sicheren Builtin-Default aktivieren
- Policy-Schema validieren

### Betriebs-Checks

- `allow_external_changes` muss lokal gesperrt bleiben
- Notification-Wirkung muss lokal gesperrt bleiben
- Workspace-Root muss vorhanden sein

### Action-Gate-Checks

- Doctrine-Compliance
- Scope-Validation
- Blast-Radius-Validation
- Approval-Readiness
- Rollback-Readiness
- Simulations-Readiness
- Zero-Trust-Readiness
- Explainability-Minimum fuer relevante Entscheidungen
- bei SEO-, GEO- oder Content-Wirkung: semantische und generative Kompatibilitaetspruefung

## Statuslogik

### `observe_only`

- lokale oder interne Schritte ohne externe Wirkung und ohne Anwendungspfad
- sicherer Default bei Unsicherheit, fehlenden Inputs, fehlenden Secrets, unklarer Ownership oder unklarem Blast Radius

### `blueprint_ready`

- lokal beschriebene Schritte mit ausreichender Form, aber ohne Laufzeitanwendung

### `approval_required`

- jeder externe Schritt ohne Freigaben, Secrets oder komplette Simulations-/Validierungsdaten

### `blocked`

- jeder Schritt mit Doktrinverstoss, ungueltigem Scope, geblocktem Blast Radius oder fehlendem Rueckweg

## Validierungswirkung im Cycle

Der Cycle fuehrt jetzt zusaetzliche lokale Validierungen:

- `doctrine_policy_schema_valid`
- `doctrine_external_changes_locked`
- `doctrine_notifications_locked`
- `doctrine_workspace_root_valid`

Fehlschlaegt eine dieser Pruefungen, wird der Cycle lokal degradiert, ohne externe Wirkung zu entfalten.

## V5-Leitkonsequenz

Die Runtime-Guardrails dienen nicht nur der technischen Sperre, sondern der Durchsetzung dieser Reihenfolge:

1. beobachten
2. einordnen und analysieren
3. nur die kleinste sichere Massnahme waehlen
4. simulieren und erklaeren
5. nur innerhalb freigegebener Grenzen anwenden
6. validieren, Resilienz pruefen und dokumentieren
