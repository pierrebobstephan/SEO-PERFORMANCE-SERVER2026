# Replay Protection Prep Model

## Zweck

Dieses Dokument beschreibt die lokale Vorbereitung fuer spaeteren Replay-Schutz bei Lizenz- und Delivery-Artefakten.

## Lokal vorbereitet

- `issued_at`-Bindung
- Pflicht fuer spaeteres `expires_at`
- Nonce-Strategie als `source not yet confirmed`
- Replay-Schutz-Status als `operator_input_required`

## Noch nicht enthalten

- echter Nonce-Dienst
- echte Server-Signatur
- echte Ablaufpruefung ausserhalb lokaler Previews

## Status

- Replay-Prep: `blueprint_ready`
- reale Replay-Protection: `approval_required`
