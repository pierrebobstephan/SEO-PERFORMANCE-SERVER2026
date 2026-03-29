# Module Map

## header_cache_audit

Zweck:

- Prueft `Content-Encoding`, `Cache-Control`, Statuscodes, Antwortzeiten und spaeter weitere Header-Signale.

Inputs:

- Ziel-Domain
- freigegebene Request-Policies
- HTTP-Response-Header
- historische Header- und Timing-Daten

Outputs:

- normalisierte Header-Snapshots
- Findings zu Kompression, Caching und Drift
- Trends fuer Header-Stabilitaet

Risiken:

- Einzelmessungen koennen CDN- oder Origin-Schwankungen ueberbewerten
- falsche Interpretation dynamischer Cache-Regeln

Spaetere Erweiterungen:

- Vary-Header-Pruefung
- ETag- und Last-Modified-Pruefung
- Cookie- und Session-Ausnahmeerkennung
- Edge-vs-Origin-Vergleich

## html_structure_audit

Zweck:

- Bewertet HTML-Gewicht, Heading-Struktur, Canonical, `lang`, Viewport und spaeter DOM-Komplexitaet.

Inputs:

- HTML-Body
- extrahierte Seitensignale
- historische Markup-Baselines

Outputs:

- Struktur-Snapshots
- Findings zu H1, semantischer Struktur und HTML-Volumen
- Vergleichswerte fuer Template-Aenderungen

Risiken:

- rohe HTML-Groesse ist nur ein Proxy und nicht die ganze Frontend-Realitaet
- komplexe Builder-Templates koennen die Ursachen verschleiern

Spaetere Erweiterungen:

- DOM-Knoten-Zahl
- Anzahl tiefer Wrapper-Strukturen
- Inline-Script- und Inline-Style-Anteile
- Critical-Path-nahe Template-Erkennung

## seo_snippet_audit

Zweck:

- Bewertet Title, Meta Description, Robots und spaeter Snippet-Qualitaet ueber mehrere Zielseiten.

Inputs:

- Seitensignale
- Suchintention-Heuristiken
- historische Snippet-Daten

Outputs:

- Snippet-Snapshots
- Laengen- und Qualitaets-Findings
- spaeter priorisierte Content-Vorschlaege

Risiken:

- reine Laengenheuristiken koennen gute Inhalte falsch einstufen
- Branding-Sonderfaelle koennen pauschale Regeln unterlaufen

Spaetere Erweiterungen:

- Duplicate-Snippet-Erkennung
- Query-/Intent-Cluster
- Search-Console-Abgleich
- Vorschlagsgenerator fuer sichere Snippet-Optimierungen

## sitemap_coverage_audit

Zweck:

- Bewertet Erreichbarkeit, spaeter Vollstaendigkeit, URL-Abdeckung und Template-Konsistenz der Sitemap.

Inputs:

- Sitemap-URL oder Sitemap-Index
- Statuscodes
- spaeter XML-Inhalte und Stichproben wichtiger URLs

Outputs:

- Coverage-Status
- Crawl- und Discovery-Findings
- URL-Abdeckungsmetriken

Risiken:

- grosse Sitemaps koennen Sampling brauchen
- erreichbar bedeutet nicht inhaltlich korrekt

Spaetere Erweiterungen:

- URL-Zaehlungen
- Lastmod-Qualitaet
- Sitemap-vs-Canonical-Abgleich
- Stichprobenbasierter Template-Vergleich zwischen Startseite und Kernseiten

## trend_engine

Zweck:

- Erkennt Drift, Stabilitaet, Ausreisser, Wiederholungen und Baseline-Veraenderungen.

Inputs:

- historische Metriken
- Ziel-Snapshots
- Rollup-Zeitfenster

Outputs:

- Trend-Richtung
- Delta-Werte
- Stabilitaets- und Vertrauenssignale

Risiken:

- zu kleine Stichproben erzeugen Scheintrends
- Tageszeit- oder Last-Effekte koennen Trends verfaelschen

Spaetere Erweiterungen:

- Varianz und Perzentile
- Saison- und Wochentagsmuster
- Change-Point-Erkennung
- Differenzierung zwischen Rauschen und echter Regression

## change_planner

Zweck:

- Uebersetzt priorisierte Findings in konkrete, reversible, spaeter connector-faehige Massnahmen.

Inputs:

- Findings
- Trends
- Risikoregeln
- Zielsystem-Zuordnung: Cloudflare, WordPress oder Observe-only

Outputs:

- Change-Blueprints
- Rollback-Definitionen
- Validierungskriterien

Risiken:

- falsche Systemzuordnung
- zu grob geschnittene Massnahmen ohne saubere Ruecknahme

Spaetere Erweiterungen:

- Change-Templating
- Abhaengigkeitsgraphen
- Batching kleiner kompatibler Massnahmen
- Preview von Vorher/Nachher-Hypothesen

## validation_engine

Zweck:

- Legt fest, wie Erfolg oder Misserfolg messbar geprueft wird, bevor irgendetwas spaeter angewendet wird.

Inputs:

- Vorher-Snapshots
- Zielmetriken
- Schwellwerte
- Validierungsfenster

Outputs:

- technische und fachliche Success-Criteria
- Stop- und Rollback-Trigger
- Validierungsberichte

Risiken:

- zu kurze Validierungsfenster
- Erfolg nur auf einer Kennzahl statt als Gesamtbild

Spaetere Erweiterungen:

- mehrstufige Gate-Validierung
- A/B-artige Pilotvalidierung
- Regression-Checks fuer Nachbarsignale
- Zeitfenster-abhaengige Bewertungslogik

## learning_engine

Zweck:

- Verdichtet Historie zu Regeln, Gewichtungen, Vertrauenswerten und Risikohinweisen.

Inputs:

- Runs
- Findings
- Trends
- Validierungsergebnisse
- Rollback-Ergebnisse

Outputs:

- Learning-Notizen
- Anpassung von Prioritaetsgewichten
- Risiko- und Erfolgswahrscheinlichkeiten

Risiken:

- Ueberlernen auf kleine Datenmengen
- falsche Verallgemeinerung aus Sonderfaellen

Spaetere Erweiterungen:

- Heuristik-Versionierung
- Explainability fuer Gewichtsveraenderungen
- getrennte Lernpfade fuer Cloudflare und WordPress
- automatisierte Erkennung unzuverlaessiger Regeln

## reporting_engine

Zweck:

- Macht Rohdaten, Trends, Prioritaeten, Plaene und spaeter Validierungsergebnisse operator-faehig.

Inputs:

- Runs
- Rollups
- Learning-Notizen
- Change-Blueprints

Outputs:

- `latest` Reports
- Rollups
- Prioritaetsberichte
- Change- und Validierungsberichte

Risiken:

- zu viele Daten ohne klare Priorisierung
- Vermischung von Beobachtung und Empfehlung

Spaetere Erweiterungen:

- Zielgruppen-spezifische Reports
- diff-orientierte Reports
- Incident- und Weekly-Summaries
- Freigabevorlagen fuer Operatoren

## approval_gate

Zweck:

- Trennt Beobachtung, Blueprint, Freigabepflicht und spaetere Anwendung.

Inputs:

- Change-Blueprints
- Policies
- Connector-Berechtigungen
- Risiko- und Reversibilitaetsbewertung

Outputs:

- Status wie `observe_only`, `blueprint_ready`, `approval_required`, `pilot_ready`, `blocked`
- Begruendung fuer Gate-Entscheidungen

Risiken:

- zu lockere Regeln lassen riskante Massnahmen durch
- zu starre Regeln blockieren sichere Quick Wins

Spaetere Erweiterungen:

- rollenbasierte Freigaben
- Mehr-Augen-Prinzip
- Connector-spezifische Gates
- automatische Sperre bei schlechter Datenqualitaet
