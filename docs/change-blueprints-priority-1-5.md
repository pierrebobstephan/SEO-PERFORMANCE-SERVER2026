# Change Blueprints Priority 1-5

## 1. Meta Description verbessern

### Ziel

- Homepage-Description spaeter ueber einen WordPress-Plugin-Pfad inhaltlich und laengenbezogen verbessern

### Beobachtung

- aktuelle Description hat `40` Zeichen

### Vermutete Ursache

- SEO-Feld, Theme oder Plugin liefert eine zu knappe Description

### Spaeterer Ziel-Connector

- `WordPress plugin`

### Inputs

- freigegebener Homepage-Scope
- Klarheit, welches SEO-Plugin oder welcher Theme-Pfad die Description steuert
- inhaltliche Freigabe fuer die neue Description

### Risiken

- doppelte oder widerspruechliche Snippet-Logik

### Validierung

- `meta_description_length` bewegt sich in einen sinnvollen Zielbereich
- Description bleibt thematisch passend
- Title, Robots und Canonical bleiben stabil

### Rollback

- Rueckkehr zur vorherigen Description-Quelle oder zum dokumentierten Vorwert

## 2. H1-Konsolidierung

### Ziel

- eine klare primaere H1 auf der Homepage

### Beobachtung

- aktueller Live-Report zeigt `H1 count: 2`

### Vermutete Ursache

- Theme, Builder oder Plugin verwendet mehrere Headlines auf gleicher Ebene

### Spaeterer Ziel-Connector

- `WordPress plugin`

### Inputs

- lokalisierter Template-, Builder- oder Plugin-Bereich
- Bestaetigung, welche Ueberschrift die primaere H1 sein soll

### Risiken

- semantische oder visuelle Verschiebung

### Validierung

- `h1_count` wird `1`
- keine ungewollte Aenderung an Title, Meta Description oder Layout

### Rollback

- Heading-Struktur auf Vorzustand setzen

## 3. HTML-Gewicht reduzieren

### Ziel

- HTML-Ausgabemenge der Homepage spaeter verringern

### Beobachtung

- `html_bytes` ist ueber mehrere Samples konstant hoch

### Vermutete Ursache

- Theme-, Builder- oder Plugin-Ausgabe erzeugt zu viel serverseitiges Markup

### Spaeterer Ziel-Connector

- `WordPress plugin`

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

## 4. Strukturbezogene SEO-Verbesserungen

### Ziel

- homepage-nahe Struktur-, Semantik- und Markup-Signale spaeter ueber einen Plugin-Pfad ordnen

### Beobachtung

- Description, H1 und HTML-Menge zeigen gemeinsam Strukturpotenzial

### Vermutete Ursache

- Theme-, Builder- oder SEO-Plugin-Ausgabe ist eher layout- als signalorientiert aufgebaut

### Spaeterer Ziel-Connector

- `WordPress plugin`

### Inputs

- freigegebener Homepage-Scope
- Klarheit ueber Theme, Builder und SEO-Plugin
- definierte Strukturziele

### Risiken

- Mehrfachlogik fuer SEO-Signale
- Nebeneffekte auf Template-Struktur

### Validierung

- H1, Description, Title, Canonical und robots bleiben konsistent
- keine neue doppelte SEO-Ausgabe

### Rollback

- Rueckkehr zum dokumentierten Vorzustand der betroffenen Ausgabequelle

## 5. Content-Encoding / Kompression

### Ziel

- textbasierte Homepage-Responses spaeter komprimiert ausliefern

### Beobachtung

- aktueller Live-Report zeigt kein `Content-Encoding`
- HTML-Groesse liegt bei `183759 bytes`

### Vermutete Ursache

- Edge- oder Origin-Kompression fuer HTML ist nicht aktiv oder nicht wirksam

### Spaeterer Ziel-Connector

- `Cloudflare secondary path`

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
