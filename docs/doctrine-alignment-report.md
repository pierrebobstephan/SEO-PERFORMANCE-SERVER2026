# Doctrine Alignment Report

## Zweck

Dieser Bericht spiegelt die neue Oberdoktrin aus [AGENTS.md](/opt/electri-city-ops/AGENTS.md), der kanonischen Langfassung in [docs/system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md) und der integrierten 8.0-Quellfassung [Doktrin04.04.2026-Version-8.0.txt](/opt/electri-city-ops/Doktrin04.04.2026-Version-8.0.txt) gegen Suite, Plugin, Fulfillment, Billing, Webhook-, Delivery- und Produktisierungslogik.

## 8.0-Deltas gegen die bisherige Basis

- formales AI-Management-System statt nur harter Runtime-Guardrails
- Pflichtinventar aller AI-, Agenten-, Tool- und Connector-Systeme
- Risikoklassen `R0` bis `R4`
- Pflicht-Impact-Assessment
- Daten-, Retrieval-, Provenance- und Supply-Chain-Governance
- staerkere Governance fuer Model-, Prompt-, Policy-, Memory- und Agent-Layer
- lebenszyklusweite Pflichten von `govern` bis `archive_delete`

## Bereits an 8.0 ausgerichtet

- Workspace-Grenzen, Rocket-Cloud-Sperre, Approval-Pflicht und `observe_only` als Default bleiben erhalten.
- Plugin, protected fulfillment, webhook runtime und public portal bleiben fail-closed und nicht-oeffnend.
- Customer- und Buyer-Sichten bleiben guarded, domain-bound und approval-gated.
- Referenzpilot-, Commercial-Chain- und Productization-Gates bleiben messbar und nachvollziehbar.

## Technisch eingezogen

- [config/doctrine-policy.json](/opt/electri-city-ops/config/doctrine-policy.json) fuehrt jetzt 8.0 als Policy-Version.
- [src/electri_city_ops/doctrine.py](/opt/electri-city-ops/src/electri_city_ops/doctrine.py) erzwingt jetzt zusaetzlich:
  - AI-Systemregister-Bereitschaft
  - Impact-Assessment-Bereitschaft
  - Provenance-Bereitschaft
  - Supply-Chain-Verifikation
  - Human Oversight bei externer Wirkung
  - Risikoklassen `R0` bis `R4`
- [schemas/doctrine-policy.schema.json](/opt/electri-city-ops/schemas/doctrine-policy.schema.json) und [schemas/pilot-simulation.schema.json](/opt/electri-city-ops/schemas/pilot-simulation.schema.json) decken diese Schicht jetzt mit ab.
- [config/ai-system-register.json](/opt/electri-city-ops/config/ai-system-register.json), [config/ai-impact-assessments.json](/opt/electri-city-ops/config/ai-impact-assessments.json), [config/provenance-evidence.json](/opt/electri-city-ops/config/provenance-evidence.json) und [config/supply-chain-evidence.json](/opt/electri-city-ops/config/supply-chain-evidence.json) operationalisieren die 8.0-Pflichtartefakte jetzt als lokale Governance-Basis.
- [src/electri_city_ops/ai_governance.py](/opt/electri-city-ops/src/electri_city_ops/ai_governance.py) validiert diese Artefakte und bindet sie in `validate-config`, Local Console und Productization-Readiness ein.
- Das WordPress-Plugin traegt die 8.0-Governance jetzt sichtbar im Bridge-Profil und in der geschuetzten Admin-Sicht.

## Weiter offene 8.0-Angleichung

- tiefere Provenance-Nachweise fuer spaetere externe Live-Artefakte ausserhalb des Workspace
- formalisierte Supply-Chain-Nachweise fuer reale Signatur-, Billing- und Delivery-Aktivierung ausserhalb des lokalen Preview-Pfads
- konsistente 8.0-Sprache in aelteren Pilot-, Produkt- und Vertriebsdokumenten, die noch `v5` im Namen tragen

## Aktuelle Gate-Aussage

- Lokal ist die Suite jetzt auf 8.0 als Fundament umgestellt.
- AI-Systemregister, Impact-Assessments, Provenance- und Supply-Chain-Evidenz sind jetzt lokal als pruefbare Vertragsobjekte vorhanden.
- Externe Wirkung bleibt weiterhin `approval_required`.
- Der aktuelle Fokus verschiebt sich von reiner v5/v7-Guardrail-Haertung hin zu AI-Management-, Provenance- und Lifecycle-Vollstaendigkeit nach 8.0.
