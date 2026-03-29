# Architektur

## Ziel

Eigenstaendiger Operations-Stack fuer SEO-, Performance- und Stabilitaetsanalyse einer produktiven WordPress-Umgebung, ohne unkontrollierte Eingriffe in Fremdsysteme.

## Module

### 1. Konfiguration und Guardrails

- TOML-Konfiguration mit defensiven Defaults
- Workspace-Pfadschutz
- Observe-only-Fallback bei Unsicherheit

### 2. Analyze

- Audit: Konfigurationszustand, Betriebsfaehigkeit, Datenluecken
- SEO: Seitenstruktur, Meta-Signale, Sitemap-Basispruefung
- Performance: Antwortzeiten, Komprimierung, Header-Basispruefung
- Fehlererkennung: Fetch-Fehler, Konfigurationsfehler, wiederkehrende Stoerungen

### 3. Decide

- Priorisierung nach Severity, Confidence, Wiederholung und Risiko

### 4. Plan

- reversible Aktionsplaene
- Kennzeichnung, ob explizite Freigabe notwendig ist

### 5. Apply

- im MVP nur interne, sichere Workspace-Aktionen
- externe Aenderungen bleiben gesperrt

### 6. Validate

- Persistenz, Report-Erzeugung, Guardrail-Integritaet

### 7. Learn

- SQLite-Historie
- Wiederholungsmuster
- Rollups fuer 1, 7, 30 und 365 Tage

## Datenfluss

1. Konfiguration laden
2. Workspace sicher bootstrapen
3. Analyse ausfuehren
4. Findings priorisieren
5. Aktionsplaene erzeugen
6. nur freigegebene sichere Aktionen anwenden
7. Lauf persistieren
8. Reports und Rollups generieren
9. Validieren
10. Lernhinweise ableiten

## Schutzprinzipien

- Kein Pfad darf den Workspace verlassen.
- Kein externer Write-Pfad ohne ausdrueckliche Freigabe.
- Bei fehlenden Domains oder deaktiviertem Remote-Read arbeitet das System weiter im Beobachtungsmodus.
- Fehlerhafte oder unvollstaendige Notification-Konfiguration fuehrt nicht zum Abbruch, sondern zu dokumentierten Findings.

## Geplanter Ausbau

- gezielte Lighthouse-/Core-Web-Vitals-Adapter
- Search-Console- und Analytics-Connectoren
- freigegebene, reversible externe Optimierungsadapter
- abgesicherte interne Patch-Pipeline fuer Selbstverbesserung des Stacks

