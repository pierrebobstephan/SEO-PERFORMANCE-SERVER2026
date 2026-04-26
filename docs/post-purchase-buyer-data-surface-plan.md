# Post Purchase Buyer Data Surface Plan

## Zweck

Dieses Dokument beschreibt, welche Daten Kaeufer nach Kauf und Installation spaeter geschuetzt einsehen koennen sollen.

## Sichtbar im installierten Plugin

- Lizenz-ID
- gebundene Domain
- Domain-Match
- erlaubter Scope
- Dokumentationszugang
- geschuetzter Downloadstatus
- Health- und Guardrail-Signale
- Cutover- und Freigabestatus
- Renewal- und Failed-Payment-Lifecycle-Status
- Explainability-/Trust-Signale:
  - bounded, explainable, reversible
  - Zero-Trust-Validation aktiv
  - server-managed rollback und validation

## Spaeter optional im geschuetzten Kundenportal

- Download-Historie
- signierte Artefakt-Referenzen
- Support-Status
- Renewal- und Lizenzstatus

## Grenzen

- keine offenen Customer-Routen ohne Freigabe
- keine preis- oder rechtsseitigen Erfindungen
- keine Live-Delivery ohne protected gates

## Status

- Plan: `blueprint_ready`
- echte globale Customer-Sicht: `approval_required`
