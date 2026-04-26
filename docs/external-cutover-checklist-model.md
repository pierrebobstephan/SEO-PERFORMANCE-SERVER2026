# External Cutover Checklist Model

## Zweck

Dieses Modell sammelt die letzten externen Cutover-Schritte in einer maschinenlesbaren Checklist, ohne sie aus dem Workspace heraus auszufuehren.

## Inhalt

- PayPal-Env-Ref-Injektion
- geschuetzte Webhook-Verifikation im Zielsystem
- Signing- und Delivery-Voraussetzungen
- Support-, Billing- und Release-Verantwortung
- Abort- und Rollback-Signale

## Zustandslogik

- `local_proof_complete`
- `external_input_required`
- `external_verification_required`
- `approval_required`
- `ready_for_execution`
- `verified_in_target`

## Grenzen

- keine Secret-Injektion aus dem Workspace
- keine Webhook-Aktivierung aus dem Workspace
- keine Delivery-Freigabe aus dem Workspace
- keine Umgehung von Approval- oder Ownership-Gates

## Artefakte

- `config/external-cutover-checklist.json`
- `schemas/external-cutover-checklist.schema.json`
- `manifests/previews/final-external-cutover-package.json`

## Status

- Checklist Model: `implemented_locally`
- echte externe Ausfuehrung: `approval_required`
