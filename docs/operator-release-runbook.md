# Operator Release Runbook

## Zweck

Dieses Runbook beschreibt den lokalen, spaeteren Operator-Pfad fuer Release-Vorbereitung.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Das Runbook bleibt lokal und gate-basiert.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Runbook nicht. Jeder echte Release ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ohne gruene Gates kein Release.

## Lokale Schritte

1. Package Metadata bauen
2. Manifest Preview bauen
3. Entitlement pruefen
4. Release-Artefakt lokal zusammensetzen
5. Live-Gates pruefen
6. ohne Gruenstatus auf `approval_required` bleiben

## Status

- Release-Runbook: `blueprint_ready`
- echter Release: `approval_required`
