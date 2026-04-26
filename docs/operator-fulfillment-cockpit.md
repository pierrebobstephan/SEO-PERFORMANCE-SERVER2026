# Operator Fulfillment Cockpit

## Zweck

Dieses Dokument beschreibt die lokale, geschuetzte Operator-Sicht fuer Checkout-Prep, Zahlungsbestaetigung, Kundenfreigabe, Lizenz-Ausgabe, Install-Pack, Signed-Delivery-Prep und den naechsten Go/No-Go-Schritt pro Domain.

## Sichtbare Bereiche

- Package-Metadaten
- Checkout Record Prep
- Payment Confirmation Prep
- Invoice Confirmation Prep
- Customer Release Authorization
- Protected Customer Release Decision
- Subscription Lifecycle Prep
- Renewal Prep
- Failed Payment Recovery Prep
- Checkout To Issuance Orchestration
- Protected Customer Install Pack
- License Issuance Prep
- Signed Delivery Prep
- Delivery-Grant-Status
- Replay-Protection-Prep
- Global Sales Readiness Summary

## Grenzen

- nur lokal oder localhost-only
- keine offene Customer-Delivery
- kein Customer-Login
- keine offene Lizenz-API
- keine Produktionsfreigabe durch die Cockpit-Sicht selbst

## Status

- Cockpit: `blueprint_ready`
- reale Operator-Freigabe fuer globale Nutzer: `approval_required`
