# Customer Release Authorization Model

## Zweck

Dieses Dokument beschreibt die lokale, geschuetzte Freigabestufe zwischen bestaetigter Zahlungsvorbereitung und spaeterer Kundenbereitstellung.

## Modell

- Release-Kanal: `protected_operator_delivery_only`
- Status: `approval_required`
- Grundlage: Checkout-Record, Payment-Confirmation, License-Issuance-Prep, Signed-Delivery-Prep und Install-Pack

## Grenzen

- keine offene Delivery
- kein Customer-Login
- keine offene Lizenz-API
- keine Freigabe ohne Operator-Review
