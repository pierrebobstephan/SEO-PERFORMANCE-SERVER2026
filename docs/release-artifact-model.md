# Release Artifact Model

## Zweck

Dieses Dokument beschreibt die lokale Struktur spaeterer Release-Artefakte.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Artefakte bleiben domain-, kanal- und entitlementgebunden.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Jede spaetere Release-Ausgabe ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. `rollback` bleibt eigener Kanal und eigenes Artefaktprofil.

## Bestandteile

- Package Metadata
- Update Manifest
- Domain Entitlement
- Artifact ID
- Release Channel

## Lokale Artefakte

- `schemas/release-artifact.schema.json`
- `schemas/domain-entitlement.schema.json`
- `tools/build_release_artifacts.py`

## Status

- Release-Artefakt-Modell: `blueprint_ready`
- echte Release-Ausgabe: `approval_required`
