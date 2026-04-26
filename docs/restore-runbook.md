# Restore Runbook

## Restore auf derselben Maschine

1. Workspace-Dateien und Datenbank aus Backup oder Snapshot wiederherstellen.
2. Getrennt verwaltete Zertifikate und Secrets an ihre Zielorte zurueckbringen.
3. Konfiguration und Doctrine laden: `validate-config`.
4. Public-Portal-Konfiguration und Legal-Seiten lokal rendern.
5. Protected Routes pruefen.
6. Test-Suite lokal ausfuehren.

## Mindestvalidierung nach Restore

- Public Portal Healthcheck
- `/legal`, `/privacy`, `/terms`, `/refund`, `/contact`
- Protected Route Blocking fuer `/operator`, `/downloads/private`, `/api/license`
- `PYTHONPATH=src python3 -m electri_city_ops validate-config --config config/settings.toml`
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`

## Grenzen

- Restore ist kein automatischer Produktiv-Failover
- externe DNS-, TLS- oder Service-Aktivierungen bleiben getrennt

## Status

- Restore Runbook: `blueprint_ready`
- realer Restore auf produktiver Maschine: `approval_required`
