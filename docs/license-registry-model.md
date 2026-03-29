# License Registry Model

## Zweck

Dieses Dokument beschreibt die lokale interne Lizenz-Registry.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Eine Lizenz wird nur intern registriert, nicht extern aktiviert.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Reale Lizenzvergabe ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Registry-Zustaende bleiben defensiv und reversibel.

## Kernfelder

- `registry_id`
- `license`
- `binding_state`
- `source_role`
- `created_at`

## Schutzregeln

- keine doppelte `license_id`
- keine doppelte `bound_domain`
- keine ungueltige Domain-Bindung
- keine implizite Mehrdomain-Freigabe

## Lokale Artefakte

- `schemas/license-registry-entry.schema.json`
- `src/electri_city_ops/registry.py`

## Status

- Lizenz-Registry-Modell: `blueprint_ready`
- reale Lizenzvergabe: `approval_required`
