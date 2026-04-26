# Public Portal Internal Linking Plan

## Zweck

Dieses Dokument beschreibt die doctrine-konforme interne Linkarchitektur fuer das oeffentliche Produktportal.

## Kernwege

- Produktinteresse -> `/explore` -> `/features` oder `/buy`
- Kaufvorbereitung -> `/buy` -> `/downloads` -> `/support`
- Scope- und Lizenzfit -> `/licensing` -> `/terms` -> `/support`
- Rechtliche Klarheit -> `/legal`, `/privacy`, `/terms`, `/refund`, `/contact`

## Komponenten

- Header-Navigation fuer zentrale Produktpfade
- Footer-Legal-Navigation als stabiler Pflichtblock
- `Related pages` auf Produkt-, Audience-, Buy- und Legal-Seiten
- Breadcrumbs auf allen Nicht-Root-Seiten

## Grenzen

- keine geschuetzten Routen verlinken
- keine Login-, Checkout- oder Downloadfunktion simulieren
- keine Crosslinks, die Fulfillment vortaeuschen

## Status

- Internal Linking Plan: `blueprint_ready`
