# Public Portal Buy Page Gating Copy

## Kernaussage

`/buy` darf das Angebot klar machen, aber keine offene Delivery, Aktivierung, Login- oder Customer-Ausfuehrung suggerieren.

## Pflichtcopy

- `Licensed download access remains protected and scope-bound. Public pages describe the offer, but they do not open private delivery, login, activation, or customer execution flows.`
- `Any real license activation, package delivery, private download, protected customer access or live execution step remains approval_required.`

## Begruendung

- Schutz der Domain- und Scope-Bindung
- Validierung und Rollback bleiben vor echter Wirkung Pflicht
- keine aggressive Conversion gegen die Doctrine

## Sichtbare Folgepfade

- `/terms` fuer die oeffentliche Angebots- und Scope-Aussage
- `/licensing` fuer Domain- und Scope-Fit
- `/downloads` fuer guarded access preparation
- `/support` fuer Klaerung von Stack, Ownership und Readiness
- `/refund` fuer rechtlichen Kontext

## Status

- Buy Page Gating Copy: `blueprint_ready`
