# Automated Invoice Flow

## Ziel

Der Rechnungsfluss wird vollautomatisch vorbereitet, bleibt aber bis zum echten Cutover geschuetzt und approval-gated.

## Lokale Artefakte

- `final-real-staging-paypal-business-ops-prep.json`
- `final-real-staging-invoice-automation-prep.json`
- `final-real-staging-payment-confirmation-prep.json`
- `final-real-staging-invoice-confirmation-prep.json`

## Sequenz

1. Checkout-Record vorbereiten
2. PayPal-Business-Operations vorbereiten
3. Invoice-Draft- und Send-Flow vorbereiten
4. Zahlungsabgleich ueber Webhook- und Operator-Bestaetigung vorbereiten
5. Protected Customer Release erst nach positivem Go/No-Go

## Guardrails

- keine offene Rechnungsseite fuer Kunden
- keine automatische Kundenfreigabe ohne Zahlungs- und Rechnungsbestaetigung
- keine Seiteneffekte auf WordPress bei fehlgeschlagener Zahlung
- keine globale Scope-Ausweitung
