# WordPress Connector Blueprint

## Zielbereich

Der spaetere WordPress-Connector ist fuer kontrollierte, klar begrenzte Inhalts-, Template- und Ausgabeoptimierungen vorgesehen, vor allem:

- Meta-Description-Pruefung und spaeteres Update
- Title-Pruefung und spaeterer Template- oder SEO-Feld-Abgleich
- H1-Konsolidierung
- HTML-Gewichtsreduktion
- Markup-Bereinigung

Nicht Ziel dieses Connectors:

- ungesteuerte Core-Manipulation
- breitflaechige Plugin-Updates
- unklare refaktorierende Theme-Eingriffe ohne Rollback

## Moegliche Zielbereiche in Theme, Builder und Plugins

### Theme

- Header-Template
- Homepage-Template
- partielle Template-Teile fuer Hero, Section-Wrapper oder Heading-Struktur

### Builder

- Page-Builder-Layouts der Homepage
- Section- oder Block-Hierarchien
- redundante Wrapper und doppelte Module

### Plugins

- SEO-Plugin-Felder fuer Title und Meta Description
- Plugin-generierte Markup-Bloecke auf der Homepage
- Widgets oder Module mit hoher HTML-Last

## Benoetigte Inputs und Freigaben

### Zuerst erforderlich

- Bestaetigung, welche WordPress-Bereiche spaeter ueberhaupt veraendert werden duerfen
- Trennung zwischen Theme-, Builder- und Plugin-Verantwortung
- Bestaetigung, ob nur Homepage oder auch weitere Seitentypen betroffen sein duerfen

### Vor spaeterer Pilotanwendung erforderlich

- Connector-Zugang oder klar freigegebener Aenderungspfad
- Information, welches Theme, welcher Builder und welche SEO-Plugins aktiv sind
- Definition des minimalen Aenderungsscope
- definiertes Rollback-Fenster

## Risiken

- Layout-Regression
- unerwartete Builder-Nebeneffekte
- doppelte oder widerspruechliche Title-/Meta-Logik zwischen Theme und SEO-Plugin
- Verschiebung sichtbarer Inhalte durch Heading-Anpassungen

## Validierung

Jede spaetere WordPress-Massnahme braucht mindestens:

- Vorher-Messung fuer `html_bytes`, `title_length`, `meta_description_length`, `h1_count`, `canonical` und `response_ms`
- HTML-Snapshot-Vergleich
- 1d- und 7d-Follow-up
- bei Struktur- oder HTML-Gewichts-Massnahmen optional 30d-Beobachtung

Nachbarsignale:

- Statuscode bleibt `200`
- Canonical bleibt konsistent
- Viewport, `lang` und Robots-Meta bleiben erhalten
- Snippet-Signale und HTML-Struktur verschlechtern sich nicht ungewollt

## Rollback-Prinzip

- jede spaetere Aenderung braucht einen klaren Vorzustand fuer Theme-, Builder- oder Plugin-Ebene
- keine kombinierten Massenanpassungen ohne Einzel-Rueckweg
- bei Layout-Bruch, semantischer Regression oder stark wachsendem HTML sofort `rollback_required`

## Connector-Zustandsmodell

- `observe_only`
- `blueprint_ready`
- `approval_required`
- `pilot_ready`
- `blocked`
- `rollback_required`

## Freigabepflichtige Sonderfaelle

- Theme-Dateien mit mehreren Seitentypen
- Aenderungen mit Core- oder Child-Theme-Abhaengigkeit
- Plugin-Konfigurationen, die siteweit wirken
- Builder-Aenderungen mit unklarem Scope oder hoher visueller Kopplung

