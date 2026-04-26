# Public Portal Operator Fields Model

## Zweck

Dieses Dokument beschreibt die konfigurierbare Operator-Schicht fuer portal-sichtbare Felder.

## Ziel

Offene Portal-Felder sollen nicht mehr als harte Copy in der App liegen, sondern aus einer sauberen lokalen Konfiguration kommen.

## Konfigurationspfad

- `config/public-portal-operator.json`

## Konfigurierbare Felder

- `support_contact`
- `support_email`
- `commercial_inquiry_label`
- `commercial_inquiry_state`
- `pricing_model_state`
- `package_tiers_state`
- `access_request_state`
- `support_readiness_state`
- `commercial_readiness_state`
- `legal_readiness_state`
- `download_readiness_state`

## Regeln

- leere oder fehlende Werte fallen auf `operator input required`, `source not yet confirmed` oder `approval_required` zurueck
- die Felder sind nur darstellend
- kein Feld aktiviert Login, Download, Lizenz oder Ausfuehrung

## Status

- Operator-Fields-Modell: `blueprint_ready`
