# Rollback Profile Registry

## Zweck

Dieses Dokument beschreibt die lokale Registry fuer domaingebundene Rollback-Profile.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Rollback bleibt domain- und profilgebunden.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Reale Rollback-Verteilung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Das Profil selbst ist der Rueckweg.

## Kernfelder

- `registry_id`
- `profile`
- `registry_state`
- `created_at`

## Lookup-Regel

- Lookup ueber `bound_domain` und `rollback_profile_id`
- ohne Treffer keine spaetere aktive Wirkung

## Lokale Artefakte

- `schemas/rollback-profile-entry.schema.json`
- `src/electri_city_ops/rollback_registry.py`

## Status

- Rollback-Registry-Modell: `blueprint_ready`
- reale Rollback-Verteilung: `approval_required`
