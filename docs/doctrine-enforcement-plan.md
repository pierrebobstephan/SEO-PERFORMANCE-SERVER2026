# Doctrine Enforcement Plan

## Zweck

Dieses Dokument beschreibt die lokale technische Durchsetzung der bindenden Doktrin aus [AGENTS.md](/opt/electri-city-ops/AGENTS.md) und [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md).

## Prueffragen fuer diese Phase

1. Ist es doktrinkonform?
   Ja. Die Enforcement-Schicht haengt nur lokale Policy-, Gate-, Guardrail- und Testlogik in den Stack ein.
2. Bleibt es innerhalb des Workspace?
   Ja. Alle Artefakte liegen in `/opt/electri-city-ops`.
3. Hat es irgendeine externe Wirkung?
   Nein. Es werden keine Connectoren, Scheduler, Notifications oder Fremdsysteme aktiviert.
4. Braucht es Approval?
   Nein fuer die lokale Enforcement-Schicht selbst. Spaetere externe Schritte bleiben `approval_required` oder `observe_only`.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Rueckweg ist lokal ueber Git oder das Ruecknehmen der neuen Workspace-Artefakte moeglich.

## Zielbild

Die Doktrin soll lokal wirksam sein, auch wenn keine externen Systeme beruehrt werden. Deshalb erzwingt der Stack jetzt:

- eine bindende Policy-Datei in [doctrine-policy.json](/opt/electri-city-ops/config/doctrine-policy.json)
- ein Policy-Schema in [doctrine-policy.schema.json](/opt/electri-city-ops/schemas/doctrine-policy.schema.json)
- ein Simulationsobjekt-Schema in [pilot-simulation.schema.json](/opt/electri-city-ops/schemas/pilot-simulation.schema.json)
- Runtime-Guardrails in [doctrine.py](/opt/electri-city-ops/src/electri_city_ops/doctrine.py)
- technische Cycle-Validierungen fuer Policy, Workspace, externe Sperre und Notification-Sperre

## Lokale Enforcement-Bausteine

### Policy-Schema

- formale Pflichtfelder fuer bindende Regeln
- kanonische Dokumentreferenzen
- Scope-, Gate- und Blast-Radius-Regeln
- Pflichtfelder fuer Simulationsobjekte

### Runtime-Guardrails

- laden die lokale Policy oder einen sicheren Builtin-Default
- validieren die Policy-Struktur
- sperren externe Wirkung technisch ueber Gate-Logik
- stufen nicht freigegebene oder unklare Schritte auf `approval_required`, `blocked` oder `observe_only`

### Pilot-Gate-Checks

- Doctrine-Compliance
- Scope-Validation
- Blast-Radius-Validation
- Approval-Readiness
- Rollback-Readiness
- Simulation-Readiness

### Testschicht

- Policy-Schema-Validierung
- Scope- und Blast-Radius-Pruefung
- Gate-Entscheidungen fuer `approval_required` und `blocked`
- Cycle-Smoke-Test mit Doctrine-Validierungen

## Statusgrenzen

### Lokal technisch umgesetzt

- Policy-Laden
- Policy-Schema-Check
- Simulationsobjekt-Check
- Approval-Readiness-Check
- Rollback-Readiness-Check
- Scope-Validation
- Blast-Radius-Validation
- lokale Runtime-Validierungen im Cycle

### Bleibt nur `blueprint_ready` oder `observe_only`

- jede spaetere Connector-Aktivierung
- Cloudflare-, WordPress-, systemd-, cron- oder Notification-Anwendung
- jede echte externe Pilotdurchfuehrung ohne Freigaben, Secrets, Scope-Definition, Validierung und Rollback

## Rueckweg

- Policy-Datei, Schemas, Docs und Tests sind lokal versionierbar
- Runtime-Enforcement kann durch Ruecknahme der betroffenen Dateien und Integration im Workspace entfernt werden
- keine Ruecknahmeoperation beruehrt Betriebssystem, Rocket Cloud oder Fremdsysteme
