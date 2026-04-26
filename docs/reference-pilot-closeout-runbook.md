# Reference Pilot Closeout Runbook

## Ziel

Den Referenzpilot nicht nur zu erfassen, sondern die drei offenen Closeout-Signale sauber und nachvollziehbar zu schliessen:

- `backup_confirmation`
- `restore_confirmation`
- `source_mapping_confirmed`

## Eingaben

- `manifests/previews/reference-pilot-installed-bridge-runtime-export.json`
- `config/reference-pilot-runtime-input.json`

## Builder

```bash
PYTHONPATH=src python3 tools/build_reference_pilot_closeout_readiness.py \
  --input manifests/previews/reference-pilot-installed-bridge-runtime-export.json \
  --output manifests/previews/reference-pilot-closeout-readiness.json
```

## Pruefpunkte

1. `backup_confirmation` ist im installierten Bridge-Admin gesetzt.
2. `restore_confirmation` ist im installierten Bridge-Admin gesetzt.
3. `source_mapping_confirmed` ist aus echtem Runtime-Zustand abgeleitet.
4. `optimization_gate` ist nicht mehr `blocked`, wenn alle Closeout-Signale gruen sind.

## Entscheidungen

- `blocked`: in staging bleiben und offene Signale schliessen
- `ready_for_closeout_review`: Review und naechsten Referenzpilot-Gate-Schritt vorbereiten

## Grenzen

- kein externer Cutover
- keine automatische Freigabe
- keine Scope-Ausweitung
