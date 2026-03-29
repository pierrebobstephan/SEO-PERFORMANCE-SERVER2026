# Domain Package Entitlement Model

## Zweck

Dieses Dokument beschreibt, wie eine Domain spaeter lokal einen Download- oder Release-Anspruch modelliert bekommt.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Entitlements bleiben domain- und scopegebunden.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Jede spaetere reale Download-Freigabe ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ohne confirmed Entitlement keine reale Ausgabe.

## Kernfelder

- `entitlement_id`
- `license_id`
- `bound_domain`
- `release_channel`
- `allowed_package_version`
- `allowed_scopes`
- `approval_state`
- `issued_at`

## Lokale Artefakte

- `schemas/domain-entitlement.schema.json`
- `src/electri_city_ops/manifest_builder.py`

## Status

- Entitlement-Modell: `blueprint_ready`
- reale Download-Freigabe: `approval_required`
