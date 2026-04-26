# Hetzner Scale Up Migration Checklist

## Vor dem Umzug

- Backup-Inventory pruefen
- SQLite-Datenbank sichern
- Portal- und Deploy-Konfigurationen sichern
- Secret- und Zertifikatstransfer vorbereiten

## Auf dem Zielserver

- Runtime und Dateisystem vorbereiten
- Workspace und Deploy-Artefakte einspielen
- Config-Validierung ausfuehren
- Public-Portal-Healthcheck lokal pruefen
- Protected Routes pruefen
- Test-Suite ausfuehren

## Vor Cutover

- DNS-/TLS-Freigabe vorhanden
- Rollback-Pfad auf Altserver dokumentiert
- Reload-/Restart-Fenster geklaert

## Status

- Hetzner Scale-Up Migration Checklist: `blueprint_ready`
- realer Cutover: `approval_required`
