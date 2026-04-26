# Protected Customer Fulfillment Model

## Zweck

Dieses Dokument beschreibt den lokalen, geschuetzten Fulfillment-Pfad fuer Plugin, Manifest, Entitlement und Lizenzsicht nach dem Kauf, ohne oeffentliche Delivery, Login oder Checkout-Funktionen zu oeffnen.

## Kernprinzipien

- Fulfillment bleibt `protected_local_only`, bis reale Delivery, Signatur und Support-Faehigkeit separat freigegeben sind.
- Jede Installation bleibt domain-bound, scope-bound und rollback-aware.
- Oeffentliche Portal-Seiten beschreiben das Angebot, nicht die private Delivery.
- spaetere Signatur-, Key-Reference- und Replay-Protection-Prep bleiben getrennt von echter Delivery.
- Käuferlesbare Einsicht darf im installierten Plugin sichtbar sein, ohne Customer-Routen oder offene API zu oeffnen.

## Lokale Artefakte

- Plugin-ZIP unter `dist/staging-only/`
- Manifest-, Lizenz-, Entitlement- und Rollback-Previews unter `manifests/previews/`
- geschuetzter Install-Pack unter `manifests/previews/final-real-staging-protected-customer-install-pack.json`

## Status

- Modell: `blueprint_ready`
- reale Customer-Fulfillment-Ausgabe: `approval_required`
