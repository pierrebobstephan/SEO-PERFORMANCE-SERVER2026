# Policy Registry Model

## Zweck

Dieses Dokument beschreibt die lokale interne Policy-Registry pro Domain.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Policies bleiben domain- und scopegebunden.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Reale Policy-Auslieferung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Widerspruechliche Policies werden nicht aktivierungsfaehig.

## Kernfelder

- `registry_id`
- `license_id`
- `bound_domain`
- `release_channel`
- `policy_version`
- `default_mode`
- `allowed_scopes`
- `module_flags`
- `registry_state`
- `created_at`

## Schutzregeln

- Policy-Scopes duerfen Lizenz-Scopes nur verengen, nicht erweitern
- `bound_domain` und `license_id` muessen zur verknuepften Lizenz passen
- `default_mode` darf Sicherheit nie aufheben

## Lokale Artefakte

- `schemas/policy-registry-entry.schema.json`
- `src/electri_city_ops/registry.py`

## Status

- Policy-Registry-Modell: `blueprint_ready`
- reale Policy-Verteilung: `approval_required`
