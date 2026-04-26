# AI System Register Model

## Zweck

Dieses Artefakt operationalisiert die 8.0-Pflicht, dass kein AI-, Agenten-, Tool- oder kundennaher Runtime-Pfad ohne Registereintrag betrieben wird.

## Datei

- [config/ai-system-register.json](/opt/electri-city-ops/config/ai-system-register.json)

## Pflichtfelder pro System

- `system_id`
- `system_name`
- `version`
- `owner`
- `validator`
- `operator`
- `auditor`
- `purpose`
- `scope`
- `jurisdiction`
- `risk_class`
- `customer_near`
- `external_effects_possible`
- `impact_assessment_ref`
- `fallback_state`
- `kill_switch`
- `rollback_path`
- `data_classes`
- `monitor_signals`
- `external_write_paths`
- `layer_governance`

## Mindestbestand im Repo

- `suite_runtime_core`
- `wordpress_bridge_plugin`
- `public_portal_surface`
- `protected_paypal_webhook_receiver`
- `protected_fulfillment_chain`

## Doktrin

Fehlt ein Pflichtsystem oder ist dessen Risikoklasse, Fallback oder Layer-Governance unklar, bleibt der 8.0-Governance-Stand `blocked`.
