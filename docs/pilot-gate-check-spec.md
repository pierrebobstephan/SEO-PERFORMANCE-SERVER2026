# Pilot Gate Check Spec

## Zweck

Dieses Dokument spezifiziert die lokale Gate-Pruefung fuer spaetere Piloten, ohne eine Anwendung auszufuehren.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Die Gate-Logik folgt direkt den Guardrails aus [AGENTS.md](/opt/electri-city-ops/AGENTS.md) und [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md).
2. Bleibt es innerhalb des Workspace?
   Ja. Die Pruefung ist rein lokal.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Die Pruefung selbst nicht. Gepruefte externe Schritte enden aber oft in `approval_required`.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Rollback-Readiness ist ein Pflichtbestandteil des Gate-Checks.

## Gate-Eingabeobjekt

Ein Gate-Check braucht mindestens:

- `connector_type`
- `target_scope`
- `external_effect`
- `requires_approval`
- `approval_granted`
- `secrets_available`
- `reversible`
- `rollback_path`
- `rollback_trigger`
- `validation_ready`
- `simulation_required`
- `simulation_object`
- `blast_radius`
- `doctrine_conformant`
- `prefer_observe_only`

## Teilpruefungen

### Doctrine-Compliance

- widerspricht der Schritt AGENTS, System Doctrine oder Alignment-Report

### Scope-Validation

- ist der Scope explizit, klein und nicht global
- enthaelt er verbotene Muster
- wuerde ein lokaler Scope den Workspace verlassen

### Blast-Radius-Validation

- ist der Blast Radius bekannt
- ist er durch Policy zugelassen
- ist er nicht `high` oder `global`

### Approval-Readiness

- liegt Freigabe vor
- sind noetige Secrets vorhanden

### Rollback-Readiness

- ist der Schritt reversibel
- ist ein Rueckweg beschrieben
- ist ein Ruecknahme-Ausloeser beschrieben

### Simulationsobjekt-Check

- sind alle Pflichtfelder vorhanden
- ist die Vorher/Nachher-Idee technisch pruefbar

## Gate-Ausgabe

### `blocked`

- bei Doktrinverstoss
- bei Scope-Verstoss
- bei geblocktem Blast Radius
- bei fehlendem Rollback

### `approval_required`

- bei externer Wirkung ohne Freigaben oder Secrets
- bei unvollstaendiger externer Simulations- oder Validierungsreife

### `pilot_ready`

- nur bei externer Wirkung mit kompletter Freigabe, kompletter Simulation, kompletter Validierung und kompletter Rollback-Reife

### `observe_only` oder `blueprint_ready`

- fuer rein lokale oder noch nicht anwendungsreife Schritte ohne externe Wirkung

## Bindung an den lokalen Stack

Die referenzielle Implementierung liegt in [doctrine.py](/opt/electri-city-ops/src/electri_city_ops/doctrine.py). Externe Piloten bleiben trotz dieser Spezifikation ohne weitere Inputs und Freigaben `approval_required`, `blueprint_ready` oder `observe_only`.
