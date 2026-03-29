# Master Architecture Phase 3.5

## Zielbild des Systems

Das langfristige Zielbild ist ein separat betriebener SEO-, Performance- und Stabilitaets-Operations-Stack auf dem Hetzner-Server, der:

- produktive WordPress- und Cloudflare-Zielsysteme zunaechst rein beobachtend bewertet
- aus Historie, Trends und Validierungsergebnissen belastbare Optimierungsvorschlaege ableitet
- spaeter nur ueber klar getrennte, freigegebene Aktor-Module eingreift
- jede Aenderung vorab plant, absichert, validiert und bei Fehlschlag kontrolliert zuruecknimmt
- nie das Betriebssystem, Rocket Cloud oder nicht freigegebene Fremdsysteme selbststaendig umbaut

Das Zielsystem ist damit kein "Auto-Tuner ohne Grenzen", sondern ein kontrolliertes Autonomiesystem mit harter Trennung zwischen:

- Beobachtung
- Bewertung
- Planerzeugung
- Freigabe
- Anwendung
- Validierung
- Lernen

## Langfristige Modulstruktur

Das Zielmodell besteht aus sechs Schichten.

### 1. Guardrails and Runtime Boundary

- Konfiguration
- Workspace-Isolation
- Secret-Boundary
- Connector-Freigaben
- Policy-Engine fuer erlaubte und verbotene Aktionen

### 2. Observe-only Intelligence Layer

- Header- und Cache-Audits
- HTML- und Markup-Audits
- SEO-Snippet- und Struktur-Audits
- Sitemap- und URL-Coverage-Audits
- Trend- und Drift-Erkennung
- Fehlerklassifikation

### 3. Knowledge and Learning Layer

- historische Messreihen
- Baselines je Domain, Pfad, Zeitfenster und Kategorie
- Wiederholungsmuster
- Erfolgs- und Misserfolgshistorie
- Ableitung von Heuristiken und Grenzwerten

### 4. Decision and Planning Layer

- Priorisierung von Findings
- Quick-Win-Erkennung
- Risikobewertung
- Aenderungsplanung
- Zuweisung an spaetere Ausfuehrungskanale wie WordPress oder Cloudflare

### 5. Approval and Execution Layer

- approval_gate
- manuell oder spaeter policy-gesteuert freigegebene Change-Pakete
- getrennte Connectoren fuer Cloudflare und WordPress
- keine direkte Ausfuehrung ohne valide Freigabe und Rollback-Pfad

### 6. Validation and Reporting Layer

- Vorher/Nachher-Vergleiche
- technische und fachliche Validierung
- Rollup-Reports
- Change-Reports
- Audit-Trail

## Datenfluss

Der langfristige Datenfluss bleibt explizit phasengetrennt.

1. Guardrails laden Konfiguration, Zielbereiche und Policies.
2. Observe-only Module lesen Zielsignale read-only aus.
3. Rohdaten werden normalisiert, historisiert und mit Baselines verknuepft.
4. trend_engine und learning_engine berechnen Drift, Stabilitaet, Wiederholung und Vertrauensgrad.
5. change_planner uebersetzt Findings in konkrete, reversible Massnahmen.
6. approval_gate bewertet, ob die Massnahme rein beobachtend bleibt, als Blueprint gespeichert wird oder spaeter freigabepflichtig ist.
7. validation_engine definiert vor der Anwendung die Erfolgskriterien und den Rollback-Pfad.
8. reporting_engine erzeugt operator-taugliche Reports, Management-Summaries und technische Detailberichte.
9. learning_engine aktualisiert Regeln, Schwellenwerte und Erfolgswahrscheinlichkeiten aus den Ergebnissen.

## Lern- und Entscheidungslogik

Das System soll nicht nur Einzelbefunde sammeln, sondern aus stabilen Mustern lernen.

### Lernlogik

- jede Messung wird einem Scope zugeordnet: System, Domain, Pfad, Connector oder Change-Paket
- Trends werden je Zeitfenster und je Signaltyp ausgewertet
- wiederkehrende Abweichungen erhalten mehr Gewicht als Einzelspitzen
- erfolgreiche spaetere Optimierungen erhoehen das Vertrauen in aehnliche kuenftige Plaene
- fehlgeschlagene oder zurueckgerollte Aenderungen senken die Wahrscheinlichkeit fuer aggressive Wiederholungen

### Entscheidungslogik

- niedrige Datenqualitaet fuehrt zu Beobachtung, nicht zu Eingriff
- hohe Wirkung ohne klare Reversibilitaet fuehrt zu Freigabepflicht
- hohe Wirkung plus niedrige technische Komplexitaet plus gute Messbarkeit kennzeichnet Quick Wins
- jede geplante Massnahme braucht klare Besitzlogik: Cloudflare, WordPress oder Observe-only

## Trennung zwischen Beobachtung, Planung, Freigabe, Anwendung und Validierung

### Beobachtung

- nur lesen
- keine Aenderungen am Zielsystem
- Aufbau von Historie, Baselines und Trends

### Planung

- Massnahmen in strukturierte Change-Plaene uebersetzen
- Risiken, Abhaengigkeiten und Rollback benennen
- vorab Messkriterien definieren

### Freigabe

- prueft Connector-Zulassung, Zielbereich, Reversibilitaet und Berechtigungen
- trennt blueprint-faehige von freigabepflichtigen Massnahmen
- dokumentiert Verantwortung und Geltungsbereich

### Anwendung

- spaeter strikt connector-basiert
- nie direkt aus einem Audit-Modul heraus
- nur bei existierendem Rollback und vorhandener Validierungsdefinition

### Validierung

- vergleicht Vorher- und Nachher-Metriken
- nutzt feste Zeitfenster
- bewertet Nebenwirkungen auf Response-Zeit, HTML-Groesse, Header, Snippets und Stabilitaet

## Sicherheitsgrenzen

Die Sicherheitsgrenzen bleiben harte Architekturregeln.

- keine Aenderungen ausserhalb `/opt/electri-city-ops`
- keine Aenderungen an Rocket Cloud
- keine Aktivierung von systemd, cron oder Benachrichtigungen ohne Freigabe
- keine Cloudflare- oder WordPress-Aenderungen ohne ausdrueckliche Connector-Freigabe
- keine selbststaendige OS-, Firewall-, Paket- oder Service-Manipulation
- observe_only bleibt der Default-Fallback bei Unsicherheit, fehlenden Zugangsdaten oder widerspruechlichen Signalen

## Rollback-Prinzip

Rollback ist kein optionaler Zusatz, sondern Teil des Zielmodells.

- jede spaetere aendernde Massnahme braucht einen dokumentierten Vorzustand
- jede Massnahme braucht eine eindeutige Ruecknahmeoperation
- jede Massnahme braucht eine Validierungsfrist
- bei ausbleibender Verbesserung oder Nebenwirkungen wird automatisch auf rollback_required gesetzt
- learning_engine speichert, welche Rollbacks erfolgreich, unvollstaendig oder unklar waren

## Schnittstellen zu Cloudflare, WordPress und reinem Observe-only Monitoring

### Cloudflare Interface

Zweck:

- spaeteres Management von Kompression, Edge-Caching, Header-Regeln und Routing-bezogenen Performance-Massnahmen

Im Phase-3.5-Zielmodell:

- rein als spaetere Connector-Schicht beschrieben
- aktuell keine Aktivierung oder Schreiboperation

Noetige Sicherheitsregeln:

- nur freigegebene Zonen
- nur definierte Regeltypen
- dry-run- oder preview-faehige Planobjekte
- Rueckbau jedes Regelsets muss bekannt sein

### WordPress Interface

Zweck:

- spaeteres Management von Meta-Daten, Template-Struktur, Theme-Anpassungen, Builder-Ausgabe und Plugin-bezogenen SEO-/Performance-Massnahmen

Im Phase-3.5-Zielmodell:

- nur als Architekturpfad und Verantwortungsbereich beschrieben
- aktuell keine Theme-, Plugin- oder Inhaltsaenderung

Noetige Sicherheitsregeln:

- nur freigegebene Zielbereiche
- keine Core-Manipulation ohne explizite Sonderfreigabe
- nur reversible Aenderungspakete
- Validierung ueber Vorher/Nachher-Crawls und technische Smoke-Checks

### Observe-only Monitoring Interface

Zweck:

- fortlaufende, sichere Datenerhebung
- Baseline-Aufbau
- Trend- und Anomalieerkennung
- Vorbereitung spaeterer Blueprints

Im Phase-3.5-Zielmodell:

- zentrale, immer aktive Grundschicht
- darf auch langfristig ohne Schreibrechte nuetzlich bleiben
- ist Referenzquelle fuer Freigabe, Validierung und Rollback-Bewertung

## Architekturfolgerung fuer Phase 4

Phase 4 sollte nicht direkt "Optimierungen bauen", sondern zuerst:

- modulweise Blueprints festlegen
- Connector-Grenzen formalisieren
- Freigabeobjekte definieren
- Validierungs- und Rollback-Schemata konkretisieren
- die observe_only Schicht weiter verdichten, damit spaetere Eingriffe datenbasiert und nicht vermutet sind

