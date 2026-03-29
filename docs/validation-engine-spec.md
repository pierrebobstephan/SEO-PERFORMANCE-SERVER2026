# Validation Engine Spec

## Zweck

Die validation_engine definiert, wie spaetere Connector-Massnahmen technisch und fachlich bewertet werden.

## Erfolgskriterien

Jede spaetere Massnahme braucht:

- mindestens eine Primaermetrik
- definierte Nachbarsignale
- Zeitfenster fuer Sofort-, Kurz- und optionale Langvalidierung
- klare Stop- und Abbruchregeln

## Vorher/Nachher-Messung

### Pflicht vor jeder spaeteren Anwendung

- identische oder vergleichbare Observe-only-Messung vor dem Eingriff
- Snapshot der relevanten Rohfelder
- Referenz auf den letzten stabilen Baseline-Zeitraum

### Pflicht nach jeder spaeteren Anwendung

- Sofort-Messung
- 1d-Messung
- 7d-Messung
- optional 30d-Messung bei strukturellen oder Cache-bezogenen Aenderungen

## Nachbarsignale

Die Primaermetrik darf nie isoliert betrachtet werden.

### Beispiele

- bessere Kompression darf nicht zu fehlerhaften Statuscodes fuehren
- bessere Cache-Werte duerfen nicht zu falscher Personalisierung fuehren
- geringeres HTML-Gewicht darf nicht die sichtbare Struktur zerstoeren
- bessere Description darf nicht Title, Canonical oder Robots unbeabsichtigt verschlechtern

## Zeitfenster 1d / 7d / 30d

### 1d

- technische Sofortstabilitaet
- schnelle Seiteneffekte
- offensichtliche Regressionssignale

### 7d

- Stabilitaet ueber mehrere Messpunkte
- erste belastbare Trendbeobachtung
- Vergleich gegen Vorher-Baseline

### 30d

- nur fuer Massnahmen mit spaeterer, trendbasierter Wirkung
- wichtig fuer Cache-, Struktur- oder groessere Template-Aenderungen

## Stop- und Abbruchkriterien

Sofortiger Abbruch oder spaeter `rollback_required`, wenn:

- Statuscode von Kernpfaden kippt
- Validierungsparser keine nutzbaren HTML-Signale mehr extrahieren koennen
- Primaermetrik ohne erkennbare Begruendung schlechter wird
- Nachbarsignale stark regressiv sind
- Blast Radius groesser ausfaellt als geplant

## Validierungsprofile pro Massnahmentyp

### Cloudflare-Kompression

- Primaermetrik: `content_encoding` vorhanden
- Nachbarsignale: `response_ms`, Statuscode, HTML-Erreichbarkeit

### Cache-Regel fuer anonyme Homepage

- Primaermetrik: kontrollierter Cache-Header oder Edge-Verhalten
- Nachbarsignale: Statuscode, Response-Zeit, HTML-Konsistenz

### HTML-Gewichtsreduktion

- Primaermetrik: `html_bytes`
- Nachbarsignale: H1, Canonical, Title, Meta Description, Statuscode

### H1-Konsolidierung

- Primaermetrik: `h1_count`
- Nachbarsignale: Title, Meta Description, HTML-Struktur

### Meta-Description-Verbesserung

- Primaermetrik: `meta_description_length` und textliche Plausibilitaet
- Nachbarsignale: Title, Robots, Canonical

## Validierungsobjekt

Jede spaetere Massnahme sollte ein Validierungsobjekt besitzen mit:

- `primary_metrics`
- `neighbor_metrics`
- `baseline_window`
- `evaluation_windows`
- `success_thresholds`
- `abort_thresholds`
- `rollback_thresholds`

