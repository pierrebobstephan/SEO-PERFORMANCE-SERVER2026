# Local Payment Confirmation Model

## Zweck

Dieses Dokument beschreibt die lokale, geschuetzte Vorbereitung fuer Zahlungsbestaetigung und Rechnungsstatus im spaeteren Kaufpfad.

## Modell

- Zahlungspfad: `PayPal Business`
- Zustand: `approval_required`
- Rechnungsstatus: lokal modelliert, nicht extern ausgestellt
- Payer- und Order-Bestaetigung: operator-gated

## Grenzen

- keine echte PayPal-API
- keine externe Zahlungsbestaetigung
- keine oeffentliche Checkout-Flaeche
- keine automatische Kundenfreigabe
