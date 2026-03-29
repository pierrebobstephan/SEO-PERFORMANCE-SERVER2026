# Plugin Module Map

## Zweck

Diese Modulkarte beschreibt die lokale WordPress-Plugin-MVP-Struktur fuer den spaeteren domaingebundenen Einsatz.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Jedes Modul hat explizite Guardrails und Rueckfallpfade.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modulmodell nicht. Spaetere Live-Nutzung pro Domain ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Jede aktive Wirkung braucht lokalen Rueckweg.

## Module

### bootstrap

- Zweck: Plugin-Start, Komponenten verdrahten, Standardmodus festlegen
- Inputs: lokale Plugin-Dateien, WordPress-Laufzeit
- Outputs: Runtime-Context, registrierte interne Komponenten
- Risiken: zu fruehe Hooks, unklare Initialisierung
- Erweiterungen: domaingebundene Konfigurationsladepfade

### license_check

- Zweck: lokalen Lizenzstatus-Snapshot lesen und Domain-Match bewerten
- Inputs: lokale Optionswerte, aktuelle Domain
- Outputs: Lizenzstatus, Kanal, Scopes, Domain-Match
- Risiken: unvollstaendige lokale Daten
- Erweiterungen: spaeter signierte License-Responses der Control Plane

### safe_mode

- Zweck: sichere Fallbacks erzwingen
- Inputs: Lizenzstatus, Konfliktlage, Runtime-Modus
- Outputs: Safe-State mit Gruenden
- Risiken: zu lockerer Fallback
- Erweiterungen: degradierte Betriebsmodi

### conflict_detection

- Zweck: SEO-, Builder- und Theme-Konflikte erkennen
- Inputs: aktive Plugins, Theme-Info
- Outputs: Konfliktstatus, Rank-Math-Hinweis, Source-Mapping-Unklarheit
- Risiken: unvollstaendige Erkennung
- Erweiterungen: feingranulare Konfliktprofile pro Plugin-Klasse

### rollback_registry

- Zweck: Rueckwege pro Modul sammeln
- Inputs: Moduldefinitionen, Before-State-Keys
- Outputs: registrierte Rollback-Eintraege
- Risiken: fehlende Before-State-Referenzen
- Erweiterungen: spaeter profilgesteuerte Rollback-Objekte

### validation_status

- Zweck: lokale Vorher/Nachher- und Nachbarsignale vorbereiten
- Inputs: Runtime-Modus, Konflikte, Lizenzstatus
- Outputs: Validation-Snapshot
- Risiken: zu geringe Signaltiefe
- Erweiterungen: DOM- und Head-Snapshot-Vergleiche

### meta_description_module

- Zweck: spaeter strikt begrenzte Homepage-Description-Logik
- Inputs: Runtime-Context, Konfliktlage, Rollback-Registry
- Outputs: aktuell nur Eligibility-Entscheidungen, spaeter Head-Hook
- Risiken: doppelte Meta-Ausgabe, unklare Source-Ownership
- Erweiterungen: exakt bestaetigte Homepage-Quellenuebernahme

### admin_screen

- Zweck: Operator-Einsicht in Status, Konflikte, Safe-Mode und Validation
- Inputs: Runtime-Context, Lizenzstatus, Konflikte, Validation-Snapshot
- Outputs: lokale Admin-Sicht
- Risiken: falsche Sicherheit durch unvollstaendige Daten
- Erweiterungen: Pilot-Checklisten und Simulationsansicht

## Status

- Modulkarte: `blueprint_ready`
- aktive Moduleffekte: `approval_required`
