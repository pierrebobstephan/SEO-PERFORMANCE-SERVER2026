# Doctrine Enforcement Plan

## Zweck

Dieses Dokument beschreibt die lokale technische Durchsetzung der bindenden Doktrin aus [AGENTS.md](/opt/electri-city-ops/AGENTS.md), [docs/system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md) und [Doktrin04.04.2026-Version-8.0.txt](/opt/electri-city-ops/Doktrin04.04.2026-Version-8.0.txt).

## Zielbild

Die Doctrine-Enforcement-Schicht soll 8.0 nicht nur referenzieren, sondern lokal erzwingen:

- bindende kanonische Quellenkette
- formale Policy-Struktur
- AI-Management-Grundpflichten
- Lifecycle-Pflichten
- Risikoklassen
- Simulations- und Evidence-Pflichten
- Approval-, Rollback- und Scope-Gates

## Lokale Enforcement-Bausteine

### Policy

- [config/doctrine-policy.json](/opt/electri-city-ops/config/doctrine-policy.json)
- 8.0-Policy-Version
- kanonische Quellenkette auf AGENTS, system-doctrine, 8.0-TXT und Alignment-Report
- AI-Management-Block
- Lifecycle-Block
- erweiterte Gate- und Simulationsdefinition

### Schemas

- [schemas/doctrine-policy.schema.json](/opt/electri-city-ops/schemas/doctrine-policy.schema.json)
- [schemas/pilot-simulation.schema.json](/opt/electri-city-ops/schemas/pilot-simulation.schema.json)
- [schemas/ai-system-register.schema.json](/opt/electri-city-ops/schemas/ai-system-register.schema.json)
- [schemas/ai-impact-assessments.schema.json](/opt/electri-city-ops/schemas/ai-impact-assessments.schema.json)
- [schemas/provenance-evidence.schema.json](/opt/electri-city-ops/schemas/provenance-evidence.schema.json)
- [schemas/supply-chain-evidence.schema.json](/opt/electri-city-ops/schemas/supply-chain-evidence.schema.json)

Sie erzwingen jetzt zusaetzlich:

- `ai_management`
- `lifecycle`
- `risk_class`
- `impact_assessment_ref`
- `evidence_plan`
- `aftercare_window`
- AI-Systemregister-Artefakte
- Impact-Assessment-Artefakte
- Provenance-Evidenz
- Supply-Chain-Evidenz

### Runtime-Guardrails

- [src/electri_city_ops/doctrine.py](/opt/electri-city-ops/src/electri_city_ops/doctrine.py)
- [src/electri_city_ops/ai_governance.py](/opt/electri-city-ops/src/electri_city_ops/ai_governance.py)

Die Guardrails blockieren oder verengen Schritte jetzt auch dann, wenn:

- kein AI-Systemregister vorliegt
- kein Impact-Assessment vorliegt
- Provenance-Bereitschaft fehlt
- Supply-Chain-Verifikation fehlt
- bei externer Wirkung Human Oversight unklar ist
- die Risikoklasse fehlt oder ungueltig ist

## Statusgrenzen

### Lokal technisch umgesetzt

- Policy-Laden
- Policy-Schema-Check
- Scope-Validation
- Blast-Radius-Validation
- Rollback-Readiness
- Approval-Readiness
- Simulations-Readiness
- AI-Governance-Readiness
- lokale Runtime-Validierungen im Cycle

### Bleibt weiter nur `approval_required`, `blueprint_ready` oder `observe_only`

- reale Connector-Aktivierung
- reale Billing-/Webhook-/Delivery-Freigabe
- externe Agentenwirkung
- kundennaher produktiver Write

## Rueckweg

- Alle Enforcement-Aenderungen liegen innerhalb des Workspace.
- Rueckweg ist lokal ueber Versionskontrolle und die Ruecknahme der betroffenen Policy-, Schema-, Code- und Doku-Dateien moeglich.
- Keine Ruecknahmeoperation beruehrt Betriebssystem, Rocket Cloud oder Fremdsysteme.
