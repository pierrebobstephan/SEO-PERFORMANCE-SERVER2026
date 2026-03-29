# Plugin Pilot 1 Prefill Notes

## Zweck

Dieses Dokument erklaert, welche Felder in [operator-approval-template-plugin-pilot-1.md](/opt/electri-city-ops/docs/operator-approval-template-plugin-pilot-1.md) automatisch vorausgefuellt wurden und welche bewusst offen bleiben.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es dokumentiert nur den Stand der bekannten Informationen.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Der spaetere Pilot ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ohne Anwendung bleibt der Rueckweg Nicht-Freigabe.

## Automatisch vorausgefuellte Felder

- Betreibername: `Pierre Stephan`
- Domain: `electri-c-ity-studios-24-7.com`
- Pilotname: `Homepage Meta Description via WordPress plugin path`
- Strategiestatus: `WordPress plugin primary path`
- aktueller Gate-Status: `approval_required`
- Hetzner-Rolle als Observe-, Learning-, Validation- und Planning-System
- Rank Math als aktuelle Ist-Situation
- Hinweis, dass Rank Math spaeter kontrolliert ersetzt und nicht abrupt entfernt werden soll
- aktueller Live-Titel aus read-only Live-Beobachtung am `2026-03-29`
- letzter validierter Titel-Capture aus [latest.md](/opt/electri-city-ops/var/reports/latest.md)
- aktuelle Meta Description, Canonical und Robots aus [latest.md](/opt/electri-city-ops/var/reports/latest.md)
- Projektpositionierung aus Live-Seite und bestehender Dokumentlandschaft:
  `24/7 online radio`, `electro/electronic music`, `crypto art`, `global audience/platform`
- Validierungsfenster `Sofortcheck`, `1d`, `7d`
- Rollback-Grundidee fuer den Pilot
- drei Meta-Description-Vorschlaege und Empfehlung fuer Variante 2

## Offene Felder

- aktives Theme
- aktiver Builder
- genaue aktuelle Description-Quelle
- genaue aktuelle Title-, Canonical- und Robots-Quelle
- genauer Rank-Math-Override-Pfad fuer Homepage-Meta
- exakter spaeterer Plugin-Aenderungspfad
- bestaetigter Homepage-only Scope
- Pilot-, Validierungs- und Rollback-Verantwortung
- finale Freigabeentscheidung

## Warum diese Felder offen bleiben

- Theme und Builder sind im Repository nicht belastbar dokumentiert
- die exakte aktuelle Description-Quelle ist ohne WordPress-Quellenmapping nicht sicher bestaetigt
- Rank Math ist als aktuelle Ist-Situation bekannt, aber seine konkrete Override-Logik fuer die Homepage ist nicht bestaetigt
- direkte rohe HTTP-Reads auf die Live-Seite liefen in eine Cloudflare-Challenge; fuer sichere Planung wurden deshalb Live-Beobachtung und letzter validierter Hetzner-Report kombiniert
- doctrine-konform werden unbestaetigte Felder nicht erfunden

## Welche minimalen Betreiberangaben noch fehlen

- Homepage-only Scope ausdruecklich bestaetigen
- aktuelle Description-Quelle in WordPress bestaetigen
- Theme, Builder und SEO-Plugin-Landschaft bestaetigen
- spaeteren Plugin-Aenderungspfad bestaetigen
- Pilot-, Validierungs- und Rollback-Verantwortung benennen
- finale Freigabe fuer Plugin Pilot 1 erteilen oder ablehnen
