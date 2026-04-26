# Policy Schema

## Zweck

Dieses Dokument beschreibt die bindende 8.0-Policy-Struktur fuer die lokale Doctrine-Enforcement-Schicht.

## Aktive Dateien

- [config/doctrine-policy.json](/opt/electri-city-ops/config/doctrine-policy.json)
- [schemas/doctrine-policy.schema.json](/opt/electri-city-ops/schemas/doctrine-policy.schema.json)
- [schemas/pilot-simulation.schema.json](/opt/electri-city-ops/schemas/pilot-simulation.schema.json)

## Pflichtfelder der 8.0-Policy

### `policy_version`

- Versionskennung der lokalen 8.0-Guardrail-Policy

### `canonical_docs`

- bindende Referenzen auf `AGENTS.md`, `docs/system-doctrine.md`, `Doktrin04.04.2026-Version-8.0.txt` und `docs/doctrine-alignment-report.md`

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
- einschliesslich `safe_mode`, `controlled_apply`, `containment_mode`, `rollback_mode` und weiterer 8.0-Zustaende

### `ai_management`

- `system_register_required`
- `impact_assessment_required`
- `provenance_required`
- `supply_chain_verification_required`
- `human_oversight_required_for_external_effects`
- `risk_classes`

### `lifecycle`

- `required_stages`
- bildet den verbindlichen 8.0-Lebenszyklus von `govern` bis `archive_delete` ab

### `scopes`

- verbotene Scope-Muster
- Pflicht fuer explizite externe Scopes

### `blast_radius`

- bekannte Blast-Radius-Werte
- geblockte Blast-Radius-Werte

### `simulation`

- Pflichtfelder fuer Simulationsobjekte vor spaeteren Piloten oder externer Wirkung
- einschliesslich `risk_class`, `impact_assessment_ref`, `evidence_plan` und `aftercare_window`

## Lokale Wirkung

Die Policy steuert:

- wie lokale Gate-Entscheidungen berechnet werden
- wann externe Schritte technisch auf `approval_required` oder `blocked` fallen
- wann AI-Register-, Impact-, Provenance-, Supply-Chain- oder Human-Oversight-Luecken einen Schritt sperren
- welche kanonische Quellenkette fuer die Doktrin bindend gilt
