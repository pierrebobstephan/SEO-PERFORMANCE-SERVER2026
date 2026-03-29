# Doctrine Alignment Report

## Zweck

Dieser Bericht spiegelt die neue Oberdoktrin aus [AGENTS.md](/opt/electri-city-ops/AGENTS.md) und [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md) gegen die bereits vorhandenen Architektur-, Gate-, Validation-, Rollback- und Observe-only-Dokumente.

## Bereits konsistente Dokumente

### Verbindliche Repo-Doktrin

- [AGENTS.md](/opt/electri-city-ops/AGENTS.md)
- [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md)

Konsistent, weil:

- die eingehenden Fassungen fachlich aufgenommen und repo-konform integriert wurden
- die kanonische Langfassung und die knappe Repo-Steuerung nun dieselbe Oberdoktrin tragen
- observe_only, Connector-Zwang, Validierung, Rollback und Betriebssystemschutz explizit gemeinsam verankert sind

### Architektur und Zielbild

- [master-architecture-phase-3-5.md](/opt/electri-city-ops/docs/master-architecture-phase-3-5.md)
- [architecture.md](/opt/electri-city-ops/docs/architecture.md)

Konsistent, weil:

- Autonomie nur innerhalb harter Grenzen gedacht ist
- Beobachtung, Planung, Freigabe, Anwendung, Validierung und Lernen klar getrennt werden
- Betriebssystem-, Workspace- und Fremdsystemschutz explizit priorisiert sind

### Gate-, Validation- und Rollback-Logik

- [approval-gate-spec.md](/opt/electri-city-ops/docs/approval-gate-spec.md)
- [validation-engine-spec.md](/opt/electri-city-ops/docs/validation-engine-spec.md)
- [rollback-playbooks.md](/opt/electri-city-ops/docs/rollback-playbooks.md)
- [decision-model.md](/opt/electri-city-ops/docs/decision-model.md)

Konsistent, weil:

- externe Wirkung nur ueber Freigabe und definierte Zustaende gedacht ist
- `rollback_required` als Pflichtreaktion auf fehlerhafte Wirkung vorgesehen ist
- Nachbarsignale und Vorher/Nachher-Vergleich die defensive Schutzlogik stuetzen

### Observe-only und datengetriebener Ausbau

- [observe-only-expansion-plan.md](/opt/electri-city-ops/docs/observe-only-expansion-plan.md)
- [operations.md](/opt/electri-city-ops/docs/operations.md)
- [data-model-roadmap.md](/opt/electri-city-ops/docs/data-model-roadmap.md)

Konsistent, weil:

- `observe_only` als sicherer Default-Fallback bereits verankert ist
- die Datentiefe vor aktiver Optimierung bewusst ausgebaut werden soll
- Lernen auf Historie, Trends und defensiver Interpretation basiert

### Connector- und Change-Blueprints

- [cloudflare-connector-blueprint.md](/opt/electri-city-ops/docs/cloudflare-connector-blueprint.md)
- [wordpress-connector-blueprint.md](/opt/electri-city-ops/docs/wordpress-connector-blueprint.md)
- [change-blueprints-priority-1-5.md](/opt/electri-city-ops/docs/change-blueprints-priority-1-5.md)
- [phase-4-execution-blueprint.md](/opt/electri-city-ops/docs/phase-4-execution-blueprint.md)

Konsistent, weil:

- keine Anwendung ohne Freigabe, Validierung und Rollback vorgesehen ist
- Ziel-Connectoren klar getrennt sind
- Risiken und Rueckwege bereits als Pflichtbestandteile formuliert sind

### Pilotvorbereitung

- [pilot-candidate-1.md](/opt/electri-city-ops/docs/pilot-candidate-1.md)
- [pilot-candidate-2.md](/opt/electri-city-ops/docs/pilot-candidate-2.md)
- [pilot-readiness-checklist.md](/opt/electri-city-ops/docs/pilot-readiness-checklist.md)
- [pilot-simulation-template.md](/opt/electri-city-ops/docs/pilot-simulation-template.md)
- [missing-secrets-and-approvals.md](/opt/electri-city-ops/docs/missing-secrets-and-approvals.md)

Konsistent, weil:

- alle aktuellen Piloten weiter auf `approval_required` oder striktem Observe-only-Pfad bleiben
- die bindenden Referenzen auf AGENTS, kanonische Langfassung und Alignment-Report explizit sind
- `simulate` und `adapt` fuer Pilotvorbereitung jetzt als eigene Pflichtbestandteile dokumentiert sind

### Technische Doctrine-Enforcement-Schicht

- [doctrine-enforcement-plan.md](/opt/electri-city-ops/docs/doctrine-enforcement-plan.md)
- [policy-schema.md](/opt/electri-city-ops/docs/policy-schema.md)
- [runtime-guardrails.md](/opt/electri-city-ops/docs/runtime-guardrails.md)
- [pilot-gate-check-spec.md](/opt/electri-city-ops/docs/pilot-gate-check-spec.md)

Konsistent, weil:

- die Doktrin jetzt lokal ueber Policy-, Scope-, Blast-Radius-, Approval- und Rollback-Pruefungen technisch eingebunden ist
- externe Wirkung weiterhin technisch gesperrt bleibt und nur als `approval_required`, `blueprint_ready` oder `observe_only` modelliert wird
- Simulationsobjekte und Gate-Checks jetzt nicht nur dokumentiert, sondern lokal testbar spezifiziert sind

## Noch bestehende Luecken

### Erweiterte Gate-Zustaende sind noch nicht vollstaendig in Spezifikationen gespiegelt

Status:

- Die erweiterte Doktrin nennt zusaetzlich `local_safe_self_heal`, `active_pilot`, `stable_applied` und `degraded_safe`.

Luecke:

- [approval-gate-spec.md](/opt/electri-city-ops/docs/approval-gate-spec.md) spiegelt aktuell nur einen engeren Teil dieser Zustandslandschaft.

### Simulations- und Adaptionsschritt sind in Piloten jetzt explizit, aber noch nicht ueberall systemweit

Status:

- Die uebernommene Doktrin staerkt den Zyklus `observe -> analyze -> decide -> simulate -> apply -> validate -> learn -> adapt -> document`.

Restluecke:

- nicht alle aelteren Blueprint- oder Connector-Dokumente modellieren `simulate` und `adapt` bereits als eigene, explizite Phasen.

### Dokumentationspflicht ist kanonisch staerker als in einzelnen Spezifikationen

Status:

- Die neue Doktrin fordert ein sehr explizites Pflichtschema fuer Kontext, Scope, Hypothese, Nebeneffekte, Rollback und finalen Status.

Luecke:

- einige Phase-4- und Phase-5-Dokumente beschreiben diese Punkte inhaltlich, aber noch nicht als einheitliches Pflicht-Datenobjekt.

### Modulbindung an die Doktrin ist lokal begonnen, aber fuer reale Connector-Laufzeiten noch nicht vollstaendig

Status:

- Die Doktrin ist jetzt lokal in Policies, Schemas, Runtime-Checks und Tests verankert.

Restluecke:

- Eine spaetere Umsetzung muss dieselbe Durchsetzung noch direkt an reale Cloudflare-, WordPress- oder andere Connector-Laufzeiten koppeln, sobald solche Pfade ueberhaupt freigegeben werden.

### Wissensaustausch ist architektonisch beschrieben, aber noch nicht maximal explizit pro Modulfluss

Status:

- Modulkooperation ist in Architektur- und Modulplandokumenten vorhanden.

Luecke:

- Spaetere Spezifikationen koennen die konkreten Datenvertraege zwischen trend_engine, learning_engine, change_planner, validation_engine und reporting_engine noch staerker formalisieren.

## Module, die besonders streng an AGENTS.md und system-doctrine.md gebunden sein muessen

### approval_gate

- weil hier entschieden wird, ob Beobachtung, Freigabe, Pilot oder Blockade gilt

### validation_engine

- weil hier gemessen wird, ob eine Wirkung akzeptabel, gemischt oder rueckzunehmen ist

### rollback-Mechanik

- weil sie die letzte Schutzbarriere gegen fehlerhafte oder riskante Wirkung darstellt

### change_planner

- weil hier aus Beobachtung spaetere Wirkung wird und Scope, Risiko und Reversibilitaet korrekt modelliert werden muessen

### learning_engine

- weil Lernen nie zu aggressiver oder schlecht erklaerbarer Autonomie fuehren darf

### Cloudflare- und WordPress-Connectoren

- weil diese spaeter die reale externe Wirkung erzeugen koennen und deshalb strikt an Workspace-Grenzen, Freigabe, Validation und Rollback gebunden bleiben muessen

## Alignment-Fazit

Die bestehende Dokumentlandschaft ist inhaltlich weitgehend mit der neuen Doktrin vereinbar. Die neue Oberdoktrin schliesst vor allem die Luecke einer zentralen, verbindlichen Repo-Steuerung und einer kanonischen Langfassung fuer Autonomie, defensive Schutzlogik, Lernen, Selbstheilung und sichere Selbstoptimierung.

Fuer spaetere technische Umsetzung bleibt die wichtigste Folgeaufgabe:

- die nun lokal verankerte Doktrin spaeter mit denselben Guardrails an reale, ausdruecklich freigegebene Connector-Laufzeiten zu koppeln, ohne die Workspace- und Observe-only-Sicherheitsbasis aufzuweichen.
