# Protected Release Grant Model

## Zweck

Dieses Dokument beschreibt den lokalen Delivery-Grant, der spaeter reale Ausgabe begrenzen soll.

## Kernfelder

- `grant_id`
- `state`
- `public_delivery`
- `customer_login`
- `license_api_exposed`

## Regeln

- `public_delivery` bleibt `false`
- `customer_login` bleibt `false`
- `license_api_exposed` bleibt `false`
- echte Ausgabe ist nur mit freigegebener Signatur- und Replay-Schutz-Kette zulaessig

## Status

- Grant-Modell: `blueprint_ready`
- reale Freigabe: `approval_required`
