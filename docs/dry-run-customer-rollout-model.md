# Dry Run Customer Rollout Model

## Zweck

Dieses Dokument beschreibt den lokalen Dry-Run-Pfad fuer spaetere Kunden-Rollouts.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Dry-Run bleibt lokal und ohne Zielsystem-Wirkung.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Reale Rollouts ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Dry-Run kann jederzeit verworfen werden.

## Lokale Artefakte

- `tools/dry_run_onboarding.py`
- `src/electri_city_ops/onboarding.py`

## Status

- Dry-Run-Rollout-Modell: `blueprint_ready`
- echter Kunden-Rollout: `approval_required`
