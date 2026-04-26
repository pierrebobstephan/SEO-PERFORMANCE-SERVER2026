# Private Site Daily Email Runbook

## Ziel

Den privaten `recommend_only`-Report taeglich per Email zustellen, ohne Public-Routen oder offene Billing-/Login-Pfade zu verwenden.

## Voraussetzungen

- IONOS-SMTP-Zugang freigegeben
- Env-Datei `deploy/systemd/private-site-report.env` mit:
  - `SMTP_FROM`
  - `SMTP_USER`
  - `SMTP_PASSWORD`
- ausdrueckliche Operator-Freigabe fuer die Aktivierung des Repo-internen Service-/Cron-Beispiels

## Manueller Lauf

```bash
PYTHONPATH=src python3 tools/build_private_site_recommend_only_report.py \
  --config config/private-site-recommend-only-report.json \
  --settings config/settings.toml
```

Mit Mailversand:

```bash
PYTHONPATH=src python3 tools/build_private_site_recommend_only_report.py \
  --config config/private-site-recommend-only-report.json \
  --settings config/settings.toml \
  --send-email
```

## Aktivierungsmodelle

- konkrete `systemd`-Units im Repo:
  - `deploy/systemd/electri-city-private-site-report.service`
  - `deploy/systemd/electri-city-private-site-report.timer`
- konkreter `cron`-Eintrag im Repo:
  - `deploy/cron/electri-city-private-site-report.cron`
- `deploy/systemd/electri-city-private-site-report.service.example`
- `deploy/systemd/electri-city-private-site-report.timer.example`
- `deploy/systemd/private-site-report.env.example`
- `deploy/cron/electri-city-private-site-report.cron.example`

Diese Dateien liegen installierbar im Workspace, werden aber nicht automatisch außerhalb des Repo installiert.

## Empfohlen: systemd

Installationskommandos:

```bash
install -m 0644 /opt/electri-city-ops/deploy/systemd/electri-city-private-site-report.service /etc/systemd/system/electri-city-private-site-report.service
install -m 0644 /opt/electri-city-ops/deploy/systemd/electri-city-private-site-report.timer /etc/systemd/system/electri-city-private-site-report.timer
systemctl daemon-reload
systemctl enable --now electri-city-private-site-report.timer
```

Verifikation:

```bash
systemctl status electri-city-private-site-report.timer
systemctl list-timers electri-city-private-site-report.timer
journalctl -u electri-city-private-site-report.service -n 50 --no-pager
```

## Alternative: cron

Installationskommandos:

```bash
install -m 0644 /opt/electri-city-ops/deploy/cron/electri-city-private-site-report.cron /etc/cron.d/electri-city-private-site-report
```

Verifikation:

```bash
cat /etc/cron.d/electri-city-private-site-report
tail -n 50 /opt/electri-city-ops/var/logs/private-site-report.log
```

## Rollback

systemd:

```bash
systemctl disable --now electri-city-private-site-report.timer
rm -f /etc/systemd/system/electri-city-private-site-report.timer
rm -f /etc/systemd/system/electri-city-private-site-report.service
systemctl daemon-reload
```

cron:

```bash
rm -f /etc/cron.d/electri-city-private-site-report
```

Der Report-Builder liest `deploy/systemd/private-site-report.env` direkt als lokalen Env-Load-Point, falls die Werte nicht schon im Prozess-Environment gesetzt sind.
