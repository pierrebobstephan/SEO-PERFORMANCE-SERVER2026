# Production Cutover Checklist Flow

## Zweck

- einen klaren Team-Pfad von installiertem Staging-Plugin zu spaeterer Produktionsreife zeigen

## Checkpunkte

- Domain binding
- URL normalization
- Baseline capture
- Conflict picture
- Operator ownership inputs
- Source mapping confirmation
- Reversible stage 1 gate
- Production cutover remains approval-gated

## Wichtig

- `cutover_ready` bleibt lokal `false`, bis echte Produktionsvoraussetzungen extern freigegeben und validiert sind
- die Checkliste ist ein Team- und Operator-Werkzeug, keine automatische Freigabe
