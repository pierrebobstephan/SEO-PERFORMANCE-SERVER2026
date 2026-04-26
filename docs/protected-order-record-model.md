# Protected Order Record Model

## Zweck

Dieses Dokument beschreibt den lokalen Checkout- oder Order-Record fuer den spaeteren Kaufpfad.

## Kernfelder

- `order_id`
- `selected_plan`
- `price_line`
- `scope_line`
- `bound_domain`
- `licensed_domain_count`
- `documentation_access`
- `licensed_download_access`
- `payment_method`
- `invoice_state`
- `customer_contact_state`

## Regeln

- der Record bleibt lokal und `approval_required`
- er darf keinen echten Zahlungsabschluss vortaeuschen
- er darf keine Customer-Delivery automatisch freigeben

## Status

- Modell: `blueprint_ready`
- echter Checkout/Order-Fulfillment: `approval_required`
