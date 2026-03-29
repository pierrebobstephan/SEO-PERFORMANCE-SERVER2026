# Plugin Admin UI Model

## Zweck

Dieses Dokument beschreibt die lokale Admin-UI-Skeleton-Struktur des spaeteren WordPress-Plugins.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Die UI dient nur Transparenz und lokalen Statusblicken.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Die UI-Spezifikation nicht. Spaetere Nutzung in WordPress-Admin ist Teil der Plugin-Freigabe.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ohne Live-Einsatz bleibt Nicht-Auslieferung der Rueckweg.

## Lokale Screens

### Runtime Overview

- aktueller Modus
- aktuelle Domain
- gebundene Domain
- Release-Kanal
- Safe-State und Gruende

### License Status

- License ID
- Status
- Allowed Scopes
- Policy Channel
- Rollback Profile ID
- Domain Match

### Conflict State

- aktive SEO-Plugins
- aktive Builder
- Theme-Name
- Rank-Math-Status
- Source-Mapping-Unklarheit

### Validation Snapshot

- Primaersignale
- Nachbarsignale
- Rollback-Flag

## Default-Verhalten

- keine aktive Speicheraenderung
- keine Fernabfragen
- keine Freigabehandlung in der UI
- informative Darstellung nur fuer lokale Diagnose

## Status

- UI-Modell: `blueprint_ready`
- produktive UI-Nutzung: `approval_required`
