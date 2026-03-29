# Policy Schema

## Zweck

Dieses Dokument beschreibt die bindende Policy-Struktur fuer die lokale Doctrine-Enforcement-Schicht.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Die Policy bildet die Guardrails aus [AGENTS.md](/opt/electri-city-ops/AGENTS.md) und [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md) technisch ab.
2. Bleibt es innerhalb des Workspace?
   Ja. Policy-Datei und Schema liegen lokal in `config/` und `schemas/`.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Nein. Es ist eine interne Schutzschicht.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Rueckweg ist die lokale Ruecknahme dieser Policy-Artefakte.

## Aktive Dateien

- [doctrine-policy.json](/opt/electri-city-ops/config/doctrine-policy.json)
- [doctrine-policy.schema.json](/opt/electri-city-ops/schemas/doctrine-policy.schema.json)
- [pilot-simulation.schema.json](/opt/electri-city-ops/schemas/pilot-simulation.schema.json)

## Policy-Felder

### `policy_version`

- Versionskennung der lokalen Guardrail-Policy

### `canonical_docs`

- bindende Referenzen auf `AGENTS.md`, `docs/system-doctrine.md` und `docs/doctrine-alignment-report.md`

### `defaults`

- `fallback_gate`
- `approval_gate`

### `workspace`

- `root_only`
- `forbid_outside_workspace`
- `forbid_rocket_cloud_changes`

### `external_effects`

- `runtime_connector_activation`
- `require_approval`
- `blocked_targets`

### `gates`

- erlaubte Gate-Zustaende fuer lokale Guardrail-Entscheidungen

### `scopes`

- verbotene Scope-Muster
- Pflicht fuer explizite externe Scopes

### `blast_radius`

- bekannte Blast-Radius-Werte
- geblockte Blast-Radius-Werte

### `simulation`

- Pflichtfelder fuer Simulationsobjekte vor spaeteren Piloten

## Lokale Wirkung

Die Policy sperrt keine Dokumentation und keine lokale Analyse. Sie steuert nur:

- wie lokale Gate-Entscheidungen berechnet werden
- wann externe Schritte technisch auf `approval_required` oder `blocked` fallen
- wann Scope- oder Blast-Radius-Angaben unzulaessig sind

## Nicht freigegebene Bereiche

Die Policy ist bewusst so definiert, dass alle echten externen Massnahmen ohne weitere Inputs und Freigaben nur in:

- `observe_only`
- `blueprint_ready`
- `approval_required`

enden duerfen.
