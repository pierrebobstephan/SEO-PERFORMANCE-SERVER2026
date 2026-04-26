# AI Impact Assessment Model

## Zweck

Diese Assessments bilden die 8.0-Pflicht ab, dass vor kundennaher oder extern wirksamer Nutzung eine strukturierte Wirkungs- und Schadensanalyse vorliegt.

## Datei

- [config/ai-impact-assessments.json](/opt/electri-city-ops/config/ai-impact-assessments.json)

## Pflichtfelder

- `assessment_id`
- `system_id`
- `risk_class`
- `status`
- `summary`
- `human_oversight_state`
- `primary_harms`
- `mitigation_controls`
- `rollback_reference`
- `monitoring_reference`
- `review_cycle`

## Regel

Die `risk_class` eines Assessments muss mit dem zugehoerigen Eintrag im AI-Systemregister uebereinstimmen. Fehlende oder abweichende Assessments blockieren die 8.0-Governance-Lage.
