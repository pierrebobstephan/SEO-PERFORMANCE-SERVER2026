# Public Portal Legal Sync Plan

## Zweck

Dieses Dokument beschreibt die Synchronisierung der oeffentlichen Legal-, Privacy-, Terms-, Refund- und Contact-Seiten des Public Portals mit den bestehenden SOC-Quellseiten.

## Quellseiten

- `https://soc.electri-c-ity-studios-24-7.com/legal/`
- `https://soc.electri-c-ity-studios-24-7.com/privacy/`
- `https://soc.electri-c-ity-studios-24-7.com/terms/`
- `https://soc.electri-c-ity-studios-24-7.com/refund/`
- `https://soc.electri-c-ity-studios-24-7.com/contact/`

## Sync-Regeln

- 1:1 uebernehmen, wo die Quellaussage sauber passt
- nur presentation-level harmonisieren
- keine neuen Rechts-, Refund-, Privacy- oder Price-Behauptungen erfinden
- keine Login-, Checkout-, Lizenz- oder Download-Funktion ableiten

## Zielrouten im Public Portal

- `/legal`
- `/privacy`
- `/terms`
- `/refund`
- `/contact`
- Alias: `/impressum` mit Canonical auf `/legal`

## Status

- Legal-Sync-Plan: `blueprint_ready`
- echte Checkout-, Lizenz- oder Download-Wirkung: `approval_required`
