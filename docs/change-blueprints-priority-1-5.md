# Change Blueprints Priority 1-5

## 1. Content-Encoding / Kompression

### Ziel

- textbasierte Homepage-Responses spaeter komprimiert ausliefern

### Beobachtung

- aktueller Live-Report zeigt kein `Content-Encoding`
- HTML-Groesse liegt bei `183759 bytes`

### Vermutete Ursache

- Edge- oder Origin-Kompression fuer HTML ist nicht aktiv oder nicht wirksam

### Spaeterer Ziel-Connector

- `Cloudflare`

### Inputs

- freigegebene Zone
- erlaubte Regeltypen
- Bestaetigung der betroffenen Pfade

### Risiken

- unerwartete Edge-Interaktion
- unvollstaendige Regelwirkung

### Validierung

- `content_encoding` vorhanden
- Statuscode bleibt stabil
- `response_ms` verschlechtert sich nicht unnoetig

### Rollback

- Kompressionsregel deaktivieren oder auf Vorzustand setzen
- Sofort-Messung und 1d-Nachkontrolle

## 2. Cache-Strategie fuer anonyme Homepage

### Ziel

- kontrolliertere Cache-Strategie fuer anonyme Homepage-Aufrufe

### Beobachtung

- aktueller Live-Report zeigt `Cache-Control: no-cache`

### Vermutete Ursache

- die Homepage wird defensiv als dynamisch behandelt

### Spaeterer Ziel-Connector

- `Cloudflare`

### Inputs

- Cookie- und Session-Ausnahmen
- freigegebene Pfaddefinition
- Bestaetigung, dass nur anonyme oeffentliche Requests betroffen sind

### Risiken

- Stale-Content
- Personalisierungsprobleme

### Validierung

- Cache-Verhalten aendert sich wie geplant
- Statuscode, HTML-Struktur und Response-Zeit bleiben stabil

### Rollback

- Cache-Regel entfernen oder Vorzustand wiederherstellen
- sofortige Header- und HTML-Pruefung

## 3. HTML-Gewicht reduzieren

### Ziel

- HTML-Ausgabemenge der Homepage spaeter verringern

### Beobachtung

- `html_bytes` ist ueber mehrere Samples konstant hoch

### Vermutete Ursache

- Theme-, Builder- oder Plugin-Ausgabe erzeugt zu viel serverseitiges Markup

### Spaeterer Ziel-Connector

- `WordPress`

### Inputs

- Theme-, Builder- und Plugin-Zuordnung
- enger Zielscope auf Homepage oder definierte Templates
- Vorzustandsreferenz

### Risiken

- Layout-Regression
- Inhaltsverlust
- Builder-Nebeneffekte

### Validierung

- `html_bytes` sinkt
- Statuscode, H1, Canonical, Title und Meta bleiben plausibel

### Rollback

- Rueckkehr zum dokumentierten Vorzustand des betroffenen Zielbereichs
- anschliessende HTML- und Signalkontrolle

## 4. H1-Konsolidierung

### Ziel

- eine klare primaere H1 auf der Homepage

### Beobachtung

- aktueller Live-Report zeigt `H1 count: 2`

### Vermutete Ursache

- Theme oder Builder verwendet mehrere Headlines auf gleicher Ebene

### Spaeterer Ziel-Connector

- `WordPress`

### Inputs

- lokalisierter Template- oder Builder-Bereich
- Bestaetigung, welche Ueberschrift die primaere H1 sein soll

### Risiken

- semantische oder visuelle Verschiebung

### Validierung

- `h1_count` wird `1`
- keine ungewollte Aenderung an Title, Meta Description oder Layout

### Rollback

- Heading-Struktur auf Vorzustand setzen
- Sofortcheck auf HTML-Signale

## 5. Meta Description verbessern

### Ziel

- Homepage-Description spaeter inhaltlich und laengenbezogen verbessern

### Beobachtung

- aktuelle Description hat `40` Zeichen

### Vermutete Ursache

- SEO-Feld ist zu knapp formuliert oder generisch belegt

### Spaeterer Ziel-Connector

- `WordPress`

### Inputs

- freigegebener SEO-Zielbereich
- Bestaetigung der inhaltlichen Richtung
- Klaerung, ob Theme oder SEO-Plugin die Quelle ist

### Risiken

- doppelte oder widerspruechliche Snippet-Logik
- schwache Inhaltsqualitaet trotz laengerem Feld

### Validierung

- `meta_description_length` bewegt sich in sinnvollem Zielbereich
- Description bleibt thematisch passend
- Title, Robots und Canonical bleiben stabil

### Rollback

- Rueckkehr zur vorherigen Description-Quelle oder zum dokumentierten Vorwert
- anschliessende Snippet- und HTML-Pruefung
