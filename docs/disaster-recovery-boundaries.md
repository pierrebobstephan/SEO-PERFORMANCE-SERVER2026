# Disaster Recovery Boundaries

## Was Backups leisten

- Wiederherstellung von Code, Konfiguration, Datenbank und Reports
- Grundlage fuer Restore auf derselben Maschine
- Grundlage fuer Migration auf neuen Hetzner-Server

## Was Backups nicht leisten

- keine Live-HA
- kein automatisches horizontales Scaling
- keine Null-Ausfall-Garantie
- keine automatische Wiederherstellung externer DNS-, TLS- oder Drittanbieter-Zustaende

## Doktrinbindung

- Wiederherstellung bleibt validierungs- und rollback-orientiert
- Unsicherheit fuehrt auf `approval_required` oder `observe_only`

## Status

- Disaster Recovery Boundaries: `blueprint_ready`
