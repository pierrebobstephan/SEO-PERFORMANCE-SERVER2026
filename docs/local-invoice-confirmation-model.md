# Local Invoice Confirmation Model

## Zweck

Dieses Dokument beschreibt die lokale, geschuetzte Vorbereitung der Rechnungsbestaetigung zwischen Payment-Confirmation und spaeterer Kundenfreigabe.

## Modell

- Status: `approval_required`
- Payment-Confirmation bleibt referenziert
- Rechnungsreferenz bleibt `operator_input_required`
- echte Rechnungsbestaetigung bleibt ausserhalb des Workspace

## Grenzen

- keine echte Rechnungsstellung aus dem Workspace
- keine implizite Kundenfreigabe
- keine Oeffnung von Delivery oder Login
