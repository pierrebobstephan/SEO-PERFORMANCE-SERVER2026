# Backup And Snapshot Strategy

## Ziel

Die Suite soll auf Hetzner sauber gesichert, wiederhergestellt und spaeter auf staerkere Hardware migriert werden koennen.

## Zwingend zu sichernde Teile

- App-Code unter `src/`, `packages/`, `schemas/`, `tools/`
- Konfiguration unter `config/`
- Datenbank `var/state/ops.sqlite3`
- JSON-State unter `var/state/json/`
- Portal-Konfigurationen unter `config/public-portal*.json`
- Deploy-Artefakte unter `deploy/`
- Reports und Logs unter `var/reports/` und `var/logs/`
- Release- und Manifest-Vorschau unter `dist/` und `manifests/`

## Hetzner-Snapshot deckt ab

- Server-Image und lokale Disk-Zustaende
- App-Code, Konfiguration, lokale Datenbank und lokale Deploy-Dateien
- installierte Runtime-Umgebung der gesicherten Maschine

## Hetzner-Snapshot deckt nicht allein ab

- getrennte Zertifikats- und Secret-Wiederherstellung
- nachvollziehbare Datei- und DB-Einzelexporte
- Zero-Downtime oder Live-HA
- DNS-, TLS- oder Cutover-Aenderungen ausserhalb des Snapshots

## Zusatzexporte

- dateibasierte Workspace-Kopie
- SQLite-Datei-Export
- `var/state/json/` als lesbarer Historien-Export
- Deploy- und Config-Export fuer Nginx/systemd/Public Portal

## Status

- Backup- und Snapshot-Strategie: `blueprint_ready`
- reale Snapshot-Erstellung: `approval_required`
