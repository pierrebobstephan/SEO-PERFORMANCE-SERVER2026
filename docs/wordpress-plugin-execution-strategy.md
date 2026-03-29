# WordPress Plugin Execution Strategy

## Zweck

Dieses Dokument definiert den Strategiewechsel: Der Hetzner-Stack bleibt das doctrine-enforced Observe-, Learning-, Validation- und Planning-System, waehrend ein spaeteres WordPress-Plugin auf IONOS WordPress der primaere Umsetzungspfad fuer echte SEO- und Performance-Optimierungen wird.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es aendert nur den geplanten spaeteren Umsetzungspfad, nicht die Schutzlogik.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Spaetere Plugin-Anwendung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Der Rueckweg ist das Beibehalten von `observe_only` und das Nicht-Freigeben spaeterer Plugin-Piloten.

## Rollenverteilung

### Hetzner-Stack

- observe-only Monitoring
- Historie und Trendbildung
- Priorisierung
- Validierungsdefinition
- Rollback-Planung
- Lern- und Reporting-Schicht

### IONOS WordPress Plugin

- spaetere, eng begrenzte On-Page- und Strukturmassnahmen
- homepage-nahe SEO-Snippets
- Heading-Hierarchie
- HTML- und Markup-Kontrolle
- strukturbezogene SEO-Verbesserungen

## Warum der Plugin-Pfad jetzt primaer ist

- die aktuell priorisierten Probleme liegen vor allem in WordPress-Ausgabe, Snippets und Struktur
- H1, Description, HTML-Menge und Markup entstehen primaer im Theme-, Builder- oder Plugin-Stack
- Ursachennahe Aenderungen sind semantisch sauberer als spaetere Edge-Workarounds
- Cloudflare bleibt hilfreich, ist fuer diese On-Page-Themen aber nicht der beste erste Hebel

## Sinnvolle Reihenfolge fuer spaetere Plugin-Optimierungen

1. Meta Description
2. H1-Konsolidierung
3. strukturbezogene SEO-Verbesserungen
4. HTML-/Markup-Reduktion

## Warum diese Reihenfolge

- Meta Description ist eng, gut messbar und meist mit geringem Seiteneffektrisiko aenderbar
- H1-Konsolidierung ist klar beobachtbar, braucht aber mehr Template-Sorgfalt
- strukturbezogene SEO-Verbesserungen setzen oft voraus, dass Description und H1 sauber sind
- HTML-/Markup-Reduktion hat den groessten Eingriff in Template- und Builder-Ausgabe und kommt deshalb spaeter

## Cloudflare bleibt sekundaer

- Kompression bleibt spaeter sinnvoll
- Cache-Regeln bleiben spaeter sinnvoll
- beides wird aber nach dem Strategiewechsel nicht mehr als primaerer erster Umsetzungspfad bewertet

## Status

- Plugin-Pfad: `approval_required`
- Cloudflare-Pfade: `approval_required`
- Hetzner-Stack: `observe_only` fuer reale Wirkung, aktiv fuer Planung und Validierung
