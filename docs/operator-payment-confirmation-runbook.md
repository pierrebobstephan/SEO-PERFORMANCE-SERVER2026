# Operator Payment Confirmation Runbook

## Ziel

Vor einer spaeteren realen Kundenfreigabe muss der Operator nachvollziehbar pruefen, dass Zahlungs- und Rechnungszustand fuer die gebundene Domain konsistent sind.

## Schritte

1. Checkout-Record fuer Plan, Domain und Scope pruefen.
2. Payment-Method auf `PayPal Business` pruefen.
3. Rechnungsreferenz und Payer-Identitaet ausserhalb des Workspace bestaetigen.
4. Payment-Confirmation-Objekt lokal auf Konsistenz pruefen.
5. Erst danach Customer-Release-Authorization weitergeben.

## Grenzen

- kein echter Zahlungsaufruf aus dem Workspace
- keine automatische Rechnungsstellung
- keine implizite Delivery-Freigabe
