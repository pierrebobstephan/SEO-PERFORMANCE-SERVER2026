# Operator Subscription Lifecycle Runbook

## Ziel

Dieses Runbook beschreibt die lokale Operator-Pruefung fuer Renewal und Failed-Payment-Recovery vor spaeterer realer Aktivierung.

## Schritte

1. Subscription-Lifecycle-Prep gegen Checkout-, Invoice- und Release-Decision-Status pruefen.
2. Renewal-Prep gegen Plan, Domain und Delivery-Grenzen pruefen.
3. Failed-Payment-Recovery-Prep gegen Grace-, Release- und Support-Grenzen pruefen.
4. Reale Renewal- oder Recovery-Wirkung weiter `approval_required` halten.
