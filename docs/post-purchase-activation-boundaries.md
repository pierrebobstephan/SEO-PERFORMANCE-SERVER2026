# Post-Purchase Activation Boundaries

## Zweck

Dieses Dokument trennt die kaeuferlesbare Sicht nach Installation von realer Delivery, Aktivierung und geschuetzter Ausfuehrung.

## Erlaubt

- lokale Admin-Sicht im installierten Plugin
- Status-, Scope-, Domain- und Guardrail-Einsicht
- lokale Hinweise auf offene Inputs und naechste Freigabeschritte

## Verboten ohne Freigabe

- offene Delivery
- Customer-Login
- offene Lizenz-API
- automatische Aktivierung ueber den staging-only Scope hinaus
- globale Optimierung oder siteweite Umschreibung

## Status

- Aktivierungsgrenzen: `blueprint_ready`
- reale Freischaltung: `approval_required`
