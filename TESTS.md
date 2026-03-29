# Test Guide

## Ziel

Die Tests pruefen den Stack lokal und ohne externe Schreibzugriffe.

## Schnelllauf

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Konfiguration pruefen

```bash
PYTHONPATH=src python3 -m electri_city_ops validate-config --config config/settings.toml
```

## Einzelnen Zyklus ausfuehren

```bash
PYTHONPATH=src python3 -m electri_city_ops run-cycle --config config/settings.toml
```

## Was geprueft wird

- Guardrails fuer Workspace-Pfade
- HTML-Signalextraktion
- observe-only Smoke-Run ohne Ziel-Domain
- read-only Domain-Run gegen einen lokalen Testserver
- Rollup-Trends fuer `response_ms` und `html_bytes`
- Lernhinweise fuer aeltere observe-only Laeufe ohne Ziel-Domain

## Hinweise

- Die Tests aktivieren weder `systemd` noch `cron`.
- Die Service- und Cron-Dateien unter `deploy/` sind nur Vorlagen.
- Fuer Live-Domain-Checks werden keine Tests ausgefuehrt; diese bleiben explizite manuelle Operator-Laeufe.

