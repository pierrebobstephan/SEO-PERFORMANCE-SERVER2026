# Backend State Machine

## Zweck

Dieses Dokument beschreibt die lokale Zustandsableitung des Backend-Cores.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Die Zustandsmaschine bleibt defensiv und stoppt frueh.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Reale Produktwirkung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. `blocked`, `observe_only` und `approval_required` bleiben harte Rueckfallzustande.

## Ableitungslogik

- irgendein `blocked` -> Backend `blocked`
- irgendein `pending` -> Backend `observe_only`
- irgendein `approval_required` -> Backend `approval_required`
- alle `confirmed` -> weiterhin `approval_required` fuer reale Wirkung

## Lokale Artefakte

- `src/electri_city_ops/backend_core.py`
- `config/backend-defaults.json`

## Status

- Backend-State-Machine: `blueprint_ready`
- reale Backend-Freigabe: `approval_required`
