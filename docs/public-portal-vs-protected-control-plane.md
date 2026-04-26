# Public Portal vs Protected Control Plane

## Zweck

Dieses Dokument trennt die oeffentlichen Portal-Flaechen von geschuetzten Operator- und Control-Plane-Pfaden.

## Oeffentlich erreichbare Routen

- `/`
- `/features`
- `/security`
- `/plugin`
- `/licensing`
- `/docs`
- `/downloads`
- `/support`
- `/robots.txt`
- `/sitemap.xml`
- `/healthz`

## Geschuetzt oder nicht oeffentlich

- `/operator`
- `/admin`
- `/control-plane`
- `/console`
- `/customer`
- `/api/operator`
- `/api/license`
- `/api/customer`
- `/downloads/private`

## Regeln

- oeffentliche Routen duerfen Produktinfo, Doku-Einstieg und gated Hinweise zeigen
- geschuetzte Routen duerfen nicht offen ins Internet
- die lokale Operator-Konsole bleibt separat und localhost-only

## Status

- Route-Trennung: `blueprint_ready`
- echte protected route exposure: `approval_required`
