# Electri City Ops

Separater, defensiver SEO- und Performance-Operations-Stack fuer eine bestehende WordPress-Umgebung.

Der aktuelle Stand ist absichtlich konservativ:

- Standardmodus ist `observe_only`
- keine Aenderungen ausserhalb des Workspace
- keine externen Optimierungen ohne explizite Freigabe
- robuste Historie, Reports, Validierung und Lernpfad ab dem ersten Lauf

## Architektur in Kurzform

Der Stack arbeitet in festen Phasen:

1. `ANALYZE`
2. `DECIDE`
3. `PLAN`
4. `APPLY`
5. `VALIDATE`
6. `COMMIT` oder defensives Verwerfen
7. `LEARN`

Jeder Lauf erzeugt:

- SQLite-Historie
- JSON-Fallback-State
- Markdown- und JSON-Reports
- Tages-, 7-Tage-, 30-Tage- und 365-Tage-Auswertungen
- priorisierte Findings, Aktionsplaene und Lernhinweise

## Sicherheitsgrenzen

- alle Dateipfade werden auf den Workspace begrenzt
- externer Netzwerkzugriff ist standardmaessig deaktiviert
- externe Aenderungen sind standardmaessig deaktiviert
- bei unvollstaendiger Konfiguration bleibt das System beobachtend

## Schnellstart

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
python3 -m electri_city_ops validate-config --config config/settings.toml
python3 -m electri_city_ops run-cycle --config config/settings.toml
```

Ohne Installation funktioniert es ebenfalls:

```bash
PYTHONPATH=src python3 -m electri_city_ops validate-config --config config/settings.toml
PYTHONPATH=src python3 -m electri_city_ops run-cycle --config config/settings.toml
```

## Wichtige Dateien

- `config/settings.toml`: Betriebsmodus und Freigaben
- `docs/architecture.md`: Modulaufbau und Datenfluss
- `docs/open-questions.md`: fehlende Angaben fuer aktive Optimierung

## Noch benoetigte Angaben

Vor aktivem Betrieb und vor jeder echten externen Optimierung fehlen derzeit mindestens:

- Ziel-Domain(s)
- erlaubte Eingriffstiefe
- erlaubte Optimierungsarten
- gewuenschte Pruefintervalle
- SMTP-/Benachrichtigungsdaten
- API-Zugaenge
- gewuenschte Report-Empfaenger

