# Provenance And Supply Chain Evidence Model

## Zweck

Doktrin 8.0 verlangt getrennte Nachweise fuer Herkunft, Evidenz, Vertrauen und Lieferkette. Im Repo werden diese Nachweise lokal ueber zwei Artefakte gefuehrt:

- [config/provenance-evidence.json](/opt/electri-city-ops/config/provenance-evidence.json)
- [config/supply-chain-evidence.json](/opt/electri-city-ops/config/supply-chain-evidence.json)

## Provenance-Pflichtfelder

- `system_id`
- `source_provenance_class`
- `evidence_confidence`
- `freshness_status`
- `human_review_status`
- `synthetic_data_ratio`
- `rights_status`
- `operational_trust_class`

## Supply-Chain-Pflichtfelder

- `system_id`
- `dependency_verification_state`
- `build_provenance_state`
- `signing_state`
- `secret_handling_state`
- `delivery_state`
- `review_state`

## Regel

Provenance belegt Herkunft und Bearbeitungsweg, nicht automatisch Wahrheit. Supply-Chain-Evidenz belegt Build-, Secret-, Signing- und Delivery-Bereitschaft, nicht automatisch globale Live-Freigabe.
