# Plugin Update Check Flow

## Zweck

Dieses Dokument beschreibt den spaeteren domaingebundenen Update-Check des Plugins anhand von Kanal, Lizenz und Manifest.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Updates bleiben domain-, kanal- und rollbackgebunden.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das lokale Modell nicht. Echte Update-Auslieferung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. `rollback` bleibt eigener Kanal.

## Logik

1. Plugin liest lokalen Lizenzstatus
2. Plugin prueft domaingebundenes Manifest
3. Plugin prueft Kanalzuordnung `stable`, `pilot` oder `rollback`
4. Plugin prueft Policy- und Rollback-Referenzen
5. Nur gueltige, domaingebundene und rollbackfaehige Updates sind spaeter ueberhaupt interpretierbar

## Fallbacks

- fehlendes Manifest: `observe_only`
- ungueltiges Manifest: `safe_mode`
- Kanal- oder Scope-Mismatch: `approval_required`

## Status

- Update-Check-Modell: `blueprint_ready`
- echte Update-Checks: `approval_required`
