# Public Deployment Security Model

## Zweck

Dieses Dokument beschreibt die Sicherheitsgrenzen des oeffentlichen Produktportals.

## Grundsatz

- public portal darf oeffentlich sein
- operator, control plane, license api und customer execution duerfen nicht ungeschuetzt sein

## Schutzregeln

- App-Upstream bindet nur an `127.0.0.1`
- Reverse Proxy entscheidet ueber die oeffentliche Flaeche
- protected routes werden oeffentlich geblockt
- keine Klartext-Secrets
- keine offene Lizenz-API
- keine offene Kundenwirkung ohne Domain-, Lizenz- und Scope-Pruefung

## Status

- Sicherheitsmodell: `blueprint_ready`
- echte geschuetzte Operator-Freigabe ueber Public Internet: `approval_required`
