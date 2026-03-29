# Plugin Packaging Model

## Zweck

Dieses Dokument beschreibt den lokalen Preview-Pfad fuer Plugin-Paketbau.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Paketbau erzeugt nur lokale Preview-Metadaten.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Jede spaetere Auslieferung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ohne Upload bleibt Nicht-Auslieferung der Rueckweg.

## Lokale Artefakte

- `tools/build_plugin_package.py`
- `schemas/plugin-package-metadata.schema.json`
- `dist/README.md`

## Status

- Packaging-Modell: `blueprint_ready`
- echte Paket-Auslieferung: `approval_required`
