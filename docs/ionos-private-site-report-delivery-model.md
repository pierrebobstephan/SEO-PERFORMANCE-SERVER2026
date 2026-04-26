# IONOS Private Site Report Delivery Model

## Profil

- SMTP Host: `smtp.ionos.de`
- Port: `587`
- Transport: `STARTTLS`
- SMTP User / Sender: `pierre.stephan1@electri-c-ity-studios.com`
- Empfaenger: `pierre.stephan1@outlook.com`

## Secrets

- keine Klartext-Secrets im Repo
- lokaler Env-Load-Point: `deploy/systemd/private-site-report.env`
- Env-Refs:
  - `SMTP_FROM`
  - `SMTP_USER`
  - `SMTP_PASSWORD`

## Fail-Closed

- fehlende Env-Refs => kein Versand
- fehlende Empfaengeradresse => kein Versand
- SMTP-Fehler => kein Fallback auf andere externe Ziele
- Report bleibt lokal unter `var/reports/private-site/` erhalten
