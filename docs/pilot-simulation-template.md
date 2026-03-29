# Pilot Simulation Template

## Zweck

Dieses Dokument definiert den doctrine-konformen `simulate -> adapt`-Pfad fuer spaetere Piloten, ohne externe Wirkung auszufuehren.

Bindende Referenzen:

- [AGENTS.md](/opt/electri-city-ops/AGENTS.md)
- [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md)
- [doctrine-alignment-report.md](/opt/electri-city-ops/docs/doctrine-alignment-report.md)
- [approval-gate-spec.md](/opt/electri-city-ops/docs/approval-gate-spec.md)
- [validation-engine-spec.md](/opt/electri-city-ops/docs/validation-engine-spec.md)

## Pflichtannahme

Solange keine vollstaendigen Freigaben und Connector-Zugaenge vorliegen, bleibt jede Simulation rein dokumentarisch, lokal oder observe-only-basiert.

## Simulationsobjekt

Jeder spaetere Pilot soll vor echter Anwendung mindestens diese Felder definieren:

- `pilot_id`
- `connector_type`
- `target_scope`
- `excluded_scope`
- `baseline_window`
- `primary_metrics`
- `neighbor_signals`
- `assumed_cause`
- `expected_gain`
- `abort_conditions`
- `rollback_trigger`
- `adapt_options`
- `final_pre_apply_gate`

## Simulationsschritte

### 1. Baseline fixieren

- relevante Vorher-Daten dokumentieren
- 1d-, 7d- und falls sinnvoll 30d-Referenzen notieren
- Qualitaet und Stabilitaet der Daten bewerten

### 2. Scope einfrieren

- Zielpfad oder Zieltemplate klar benennen
- Nicht-Zielbereiche klar ausschliessen
- maximalen Blast Radius beschreiben

### 3. Hypothese pruefen

- vermutete Ursache formulieren
- alternative Ursachen notieren
- Unsicherheit bewerten

### 4. Nachbarsignale festlegen

- technische Integritaet
- Statuscode
- Header-Stabilitaet
- HTML-Struktur
- SEO-Signale
- Fehler- oder Drift-Indikatoren

### 5. Abbruch- und Adaptionslogik definieren

- wann `approval_required` bestehen bleibt
- wann `blocked` gesetzt werden muss
- wann spaeter `pilot_ready` vertretbar waere

## Connector-spezifische Hinweise

### Cloudflare

- Cookie-, Session-, Login- und Preview-Ausnahmen muessen vor jeder Anwendung dokumentiert sein
- globale Regeln ohne enge Pfadlogik sind `blocked`

### WordPress

- Theme-, Builder- oder Plugin-Zielbereich muessen eindeutig getrennt sein
- siteweite oder mehrdeutige Aenderungen ohne Einzel-Rollback sind `blocked`

## Adaptionsausgaenge

- `observe_only`: Daten reichen noch nicht oder die Unsicherheit ist zu hoch
- `approval_required`: Schritt ist doctrine-konform, aber Freigaben, Secrets oder Simulationsdaten fehlen
- `blocked`: Schritt verletzt Scope-, Risiko- oder Rollback-Grenzen
- `pilot_ready`: nur moeglich, wenn Simulationsobjekt, Freigaben, Validierungsfenster und Rollback vollstaendig sind

## Dokumentationspflicht

Jeder spaetere Pilot soll Simulation und Adaptionsentscheidung gemeinsam protokollieren mit:

- Kontext
- Ziel
- Scope
- Hypothese
- Primaermetriken
- Nachbarsignalen
- Abort-Kriterien
- Rollback-Pfad
- Gate-Status
- Begruendung
