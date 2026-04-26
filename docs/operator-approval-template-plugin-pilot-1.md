# Operator Approval Template: Plugin Pilot 1

## Status

- Betreibername: `Pierre Stephan`
- Pilotname: `Homepage Meta Description via WordPress plugin path`
- Strategiestatus: `WordPress plugin primary path`
- aktueller Gate-Status: `approval_required`
- Hetzner-Rolle: `doctrine-enforced Observe-, Learning-, Validation- und Planning-System`
- aktuelle externe Wirkung: `keine`

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Dieses Dokument sammelt nur Freigaben und Inputs fuer einen spaeteren, kleinskaligen Homepage-Pilot.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Die Vorlage selbst nicht. Der spaetere Plugin-Pilot ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Rueckkehr zur vorherigen Description-Quelle oder zum dokumentierten Vorwert.

## Referenzen

- [AGENTS.md](/opt/electri-city-ops/AGENTS.md)
- [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md)
- [Doktrin04.04.2026-Version-8.0.txt](/opt/electri-city-ops/Doktrin04.04.2026-Version-8.0.txt)
- [plugin-pilot-candidate-1.md](/opt/electri-city-ops/docs/plugin-pilot-candidate-1.md)
- [plugin-minimal-input-list.md](/opt/electri-city-ops/docs/plugin-minimal-input-list.md)
- [wordpress-plugin-execution-strategy.md](/opt/electri-city-ops/docs/wordpress-plugin-execution-strategy.md)
- [plugin-connector-priority-shift.md](/opt/electri-city-ops/docs/plugin-connector-priority-shift.md)
- [optimization-priority-report.md](/opt/electri-city-ops/docs/optimization-priority-report.md)
- [change-blueprints-priority-1-5.md](/opt/electri-city-ops/docs/change-blueprints-priority-1-5.md)
- [latest.md](/opt/electri-city-ops/var/reports/latest.md)

## Belastbar vorausgefuellte Fakten

- Domain: `electri-c-ity-studios-24-7.com`
- Ziel: `Verbesserung der Homepage Meta Description`
- geplanter Connector-Pfad: `WordPress plugin on IONOS WordPress`
- geplanter Scope: `nur Homepage`
- siteweite Freigabe: `nein`
- Rank Math Status: `aktuell aktiv`
- Rank-Math-Ablosung: `spaeter kontrolliert ersetzen, nicht abrupt entfernen`
- aktueller Live-Titel, read-only beobachtet am `2026-03-29`: `Electri_C_ity - Studios 24/7 - Global Electro Music Online Radio 24 / 7`
- letzter validierter Hetzner-Titel-Capture: `Electri_C_ity Studios | 24/7 Online Radio & Crypto Art`
- aktuelle Meta Description laut letztem validierten Live-Lauf: `Global Electro Music Online Radio 24 / 7`
- aktuelle Canonical laut letztem validierten Live-Lauf: `https://electri-c-ity-studios-24-7.com/`
- aktuelle Robots-Meta laut letztem validierten Live-Lauf: `follow, index`
- aktuelle Live-Projektpositionierung:
  `24/7 online radio`, `electro/electronic music`, `crypto art`, `global audience/platform`

## Scope- und Quellklarheit

- Homepage-only Scope freigegeben: `operator input required`
- exakter WordPress-Plugin-Aenderungspfad spaeter freigegeben: `operator input required`
- aktives Theme: `source not yet confirmed`
- aktiver Builder: `source not yet confirmed`
- genaue aktuelle Description-Quelle: `source not yet confirmed`
- genaue aktuelle Title-Quelle: `source not yet confirmed`
- genaue aktuelle Canonical-Quelle: `source not yet confirmed`
- genaue aktuelle Robots-Quelle: `source not yet confirmed`
- genauer Rank-Math-Override-Pfad fuer Homepage-Meta: `source not yet confirmed`

## Verantwortlichkeiten

- Pilot-Verantwortung: `operator input required`
- Validierungsverantwortung: `server_managed_bridge`
- Rollback-Verantwortung: `server_managed_bridge`

## Validierungslogik

- Primaermetrik: `meta_description_length`
- Nachbarsignale:
  `Title`, `Canonical`, `Robots`, `keine doppelte Meta-Ausgabe`, `keine neue HTML-Regression`
- Validierungsfenster:
  `Sofortcheck`, `1d`, `7d`
- Vorher-Nachher-Vergleich erforderlich: `ja`
- Explainability-Pflicht:
  `Warum nur diese Mikroaenderung und keine aggressivere Uebernahme?`

## Rollback-Logik

- Rueckweg:
  `Rueckkehr zur vorherigen Description-Quelle oder zum dokumentierten Vorwert`
- Sofortcheck nach Rueckweg:
  `eindeutige Meta-Ausgabe`, `stabile Homepage-Signale`
- abrupte Rank-Math-Entfernung vor validierter Ersatzlogik: `nein`
- serverseitige Durchfuehrung laut Bridge-Doktrin: `ja`

## Betreiberfreigaben

- Homepage-Scope bestaetigt: `operator input required`
- nur Meta-Description betroffen: `operator input required`
- gleichzeitige Aenderung an Title, Canonical oder Robots erlaubt: `nein`
- Rank Math darf fuer diesen Pilot aktiv bleiben: `ja`
- kontrollierter Rank-Math-Ablosungspfad spaeter akzeptiert: `operator input required`
- WordPress-Plugin-Pilot grundsaetzlich freigegeben: `operator input required`
- finale Pilotentscheidung:
  `TBD`
- Begruendung:
  `operator input required`

## Meta-Description-Vorschlaege

Nur Vorschlaege, keine Anwendung:

### Variante 1

`24/7 online radio for electro music, progressive sounds and crypto art by Electri_C_ity Studios - global stream, creative vision and digital culture.`

### Variante 2

`Electri_C_ity Studios delivers 24/7 online radio, electronic music, progressive vibes and crypto art - a global platform for sound, vision and digital creativity.`

### Variante 3

`Explore Electri_C_ity Studios: 24/7 online radio, electronic music, progressive energy and crypto art on a global platform for sound and digital culture.`

Empfohlene erste Zielversion:

- `Variante 2`

## Offene Betreiberangaben

- exakte aktuelle Description-Quelle in WordPress
- bestaetigter Homepage-only Scope
- exakter spaeterer Plugin-Aenderungspfad
- Pilot-, Validierungs- und Rollback-Verantwortung
- finale Freigabeentscheidung
