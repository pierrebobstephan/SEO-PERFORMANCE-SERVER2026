# PayPal Secret Reference Model

## Ziel

PayPal-Business-Credentials werden ausschliesslich ueber Secret-Referenzen eingebunden.

## Erlaubt

- Environment-Variablen-Referenzen
- lokale Presence-Checks
- geschuetzte Operator-Runbooks

## Verboten

- Klartext `client_id`
- Klartext `client_secret`
- Klartext `webhook_id`
- Commit von Live-Secrets in Config, Code, Tests oder Doku

## Erwartete Referenzen

- `PAYPAL_BUSINESS_CLIENT_ID`
- `PAYPAL_BUSINESS_CLIENT_SECRET`
- `PAYPAL_BUSINESS_WEBHOOK_ID`

## Validation

Die lokale Preflight-Schicht prueft nur:

- Env-Referenzen vorhanden
- Klartext-Secrets nicht im Repo
- Public Exposure bleibt deaktiviert
