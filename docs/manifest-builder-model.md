# Manifest Builder Model

## Zweck

Dieses Dokument beschreibt den lokalen Manifest-Builder fuer spaetere Update- und Download-Objekte.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es baut nur lokale Vorschau-Manifeste.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Jede spaetere Manifest-Ausgabe ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ohne bestaetigte Rollback-Referenz kein Manifest.

## Preconditions

- Lizenz-Registry-Eintrag `confirmed`
- Policy-Registry-Eintrag `confirmed`
- Rollback-Registry-Eintrag `confirmed`
- angeforderter Kanal passt zu Lizenz und Policy
- Rollback-Profil passt zur Lizenz

## Lokale Artefakte

- `schemas/manifest-build-request.schema.json`
- `src/electri_city_ops/manifest_builder.py`

## Status

- Manifest-Builder-Modell: `blueprint_ready`
- reale Manifest-Ausgabe: `approval_required`
