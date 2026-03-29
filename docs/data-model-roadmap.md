# Data Model Roadmap

## Welche Metriken bereits existieren

Aktuell existieren im Stack folgende Metrikgruppen.

### Audit-Metriken

- `configured_domains`
- `remote_fetch_enabled`
- `external_changes_enabled`
- `email_enabled`
- `cycle_interval_minutes`

### Target-Metriken

- `homepage_status_code`
- `response_ms`
- `html_bytes`
- `sitemap_status_code`
- `title_length`
- `meta_description_length`
- `h1_count`
- `has_canonical`
- `has_html_lang`
- `viewport_present`
- `compressed_response`
- `has_cache_control`
- `sitemap_available`

### Fehler- und Kontrollmetriken

- `active_findings`
- `observed_target_results`

### Bereits persistierte Rohfelder in target_snapshots

- `domain`
- `final_url`
- `homepage_status_code`
- `response_ms`
- `html_bytes`
- `content_encoding`
- `cache_control`
- `title`
- `meta_description`
- `canonical`
- `h1_count`
- `html_lang`
- `viewport_present`
- `robots_meta`
- `sitemap_status_code`
- `fetch_error`

## Welche Metriken als naechstes sinnvoll sind

Die naechste Ausbaustufe sollte die heutigen Prioritaeten besser erklaeren.

### Header and Cache

- expliziter Cache-Mode je Response
- `vary_header_present`
- `etag_present`
- `last_modified_present`
- Cookie-Praesenz auf anonymen Seiten
- spaeter Edge-Cache-Status, falls sicher auslesbar

### HTML and Structure

- DOM-Knoten-Anzahl
- Anzahl von Script-Tags
- Inline-Script-Bytes
- Inline-Style-Bytes
- Hauptinhalt-vs-Wrapper-Anteil
- Heading-Hierarchie, nicht nur H1-Zahl

### SEO and Coverage

- Title- und Description-Duplikate ueber mehrere URLs
- Anzahl indexierbarer URLs in Sitemap-Stichproben
- Canonical-vs-final-URL-Abweichungen ueber mehrere Seiten
- Robots-Meta-Klassen
- spaeter interne Linksignale auf Kernseiten

### Performance and Stability

- DNS-, Connect- und TLS-Zeiten, falls sicher trennbar
- Time to first byte, falls sauber messbar
- Antwortgroesse komprimiert vs unkomprimiert
- Fehlerraten ueber Zeitfenster
- Schwankungsbreite von `response_ms`

## Welche Feld-, Trend- und Vergleichsdaten noch fehlen

Fuer sichere Entscheidungen fehlen derzeit vor allem Kontext- und Vergleichsfelder.

### Feldluecken

- Snapshot-Felder fuer weitere Header
- URL-Typ wie Homepage, Archiv, Detailseite oder Sitemap-Index
- Quellzuordnung wie Edge, Origin oder Redirect-Kette
- Template- oder Seitentyp-Klassifikation

### Trendluecken

- Varianz, Median und Perzentile statt nur `latest`, `previous` und `delta`
- Tageszeit- und Wochentagsvergleiche
- Vergleich von Rolling Windows
- Aenderungspunkte nach spaeteren Optimierungen

### Vergleichsluecken

- Domain-vs-Pfad-Vergleich
- Homepage-vs-Stichproben-Kernseiten
- Vorher/Nachher-Vergleich auf Change-Paket-Ebene
- Vergleich zwischen freigegebenen und nicht freigegebenen Connector-Zonen

## Welche historischen Daten fuer sichere Entscheidungen noetig sind

Historie ist nicht nur Speicher, sondern Voraussetzung fuer sichere Freigaben.

### Minimum fuer beobachtende Aussagen

- mindestens 7 Tage Trendhistorie fuer wiederkehrende Messungen
- mehrere Samples pro relevantes Signal
- markierte Ausreisser und erkannte Datenluecken

### Minimum fuer Quick-Win-Blueprints

- stabile Baseline ueber 1d und 7d
- klare Primaermetrik
- mindestens ein plausibler Rollback-Indikator
- nachvollziehbarer Verantwortungsbereich

### Minimum fuer spaetere aendernde Massnahmen

- belastbare Vorher-Historie
- Nachbarsignale fuer Regressionserkennung
- dokumentierte Erfolgs- und Abbruchkriterien
- Change-Paket-Zuordnung in der Historie
- Connector-spezifische Audit-Trails

## Empfohlene Roadmap-Reihenfolge

1. Observe-only Datenqualitaet verbreitern.
2. Mehr Header- und Strukturfelder erfassen.
3. Trendengine um Varianz und Stabilitaet ergaenzen.
4. Pfad- und Seitentyp-Differenzierung einfuehren.
5. Vergleichslogik fuer spaetere Change-Pakete vorbereiten.
6. Erst danach Cloudflare- oder WordPress-Connectoren mit echten Freigabepfaden planen.

