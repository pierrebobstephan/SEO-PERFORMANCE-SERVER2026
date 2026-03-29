# Observe-only Expansion Plan

## Ziel

Die Observe-only-Schicht soll vor jeder spaeteren aktiven Optimierung datenreicher, trendstabiler und entscheidungsfaehiger werden.

## Ausbau von Header-Historie

### Ziel

- Header-Signale ueber genug Samples hinweg vergleichen koennen

### Ausbaupunkte

- `Content-Encoding`-Historie
- `Cache-Control`-Historie
- spaeter `Vary`, `ETag`, `Last-Modified`
- Kennzeichnung von Header-Schwankungen je Zeitfenster

### Prioritaet

- hoch

### Teststrategie

- lokale Parser- und Rollup-Tests
- Regressionstests fuer Trendberechnung
- kein externer Schreibzugriff

## Sitemap-Coverage

### Ziel

- nicht nur `200` bestaetigen, sondern spaeter Abdeckung und Konsistenz bewerten

### Ausbaupunkte

- URL-Zahl
- Sitemap-Index vs Einzel-Sitemap
- spaeter Stichproben wichtiger URLs
- Canonical- und Robots-Konsistenz

### Prioritaet

- hoch

### Teststrategie

- lokale Fixture-Sitemaps
- Parser-Tests fuer kleine und grosse XML-Strukturen
- defensive Limits fuer Antwortgroesse und Sampling

## Trendqualitaet

### Ziel

- Scheintrends von belastbaren Trends trennen

### Ausbaupunkte

- Varianz
- Median
- Perzentile
- Change-Point-Indikatoren
- Markierung von zu kleinen Stichproben

### Prioritaet

- hoch

### Teststrategie

- historische Fixture-Reihen
- Drift-Tests mit stabilen, verbesserten und verschlechterten Serien
- klare Erwartungen fuer `flat`, `improving`, `worsening`, `insufficient_data`

## Struktur- und DOM-Metriken

### Ziel

- HTML-Gewicht besser erklaeren und spaetere Template-Optimierungen praeziser machen

### Ausbaupunkte

- DOM-Knoten-Zahl
- Heading-Hierarchie
- Anzahl Wrapper-Ebenen
- Anzahl Script- und Style-Bloecke
- Inline-Script- und Inline-Style-Volumen

### Prioritaet

- mittel bis hoch

### Teststrategie

- lokale HTML-Fixtures mit klar erwarteten DOM- und Heading-Werten
- Regressionstests fuer Parser und Extraktoren

## Prioritaeten

1. Header-Historie
2. Trendqualitaet
3. Sitemap-Coverage
4. Struktur- und DOM-Metriken

## Teststrategie gesamt

- zuerst lokale Parser- und Trendtests
- dann Smoke-Tests gegen lokale Testserver
- erst danach weitere read-only Live-Messungen
- keine Aenderung von Connectoren, Scheduler oder externen Systemen

