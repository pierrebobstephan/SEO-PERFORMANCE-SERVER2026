# Local Checkout To Issuance Orchestration

## Zweck

Dieses Dokument beschreibt den lokalen, geschuetzten Ablauf von einem oeffentlichen Plan bis zur spaeteren Lizenz- und Delivery-Freigabe.

## Stufen

1. oeffentlichen Plan waehlen
2. lokalen Checkout-Record vorbereiten
3. Customer-Kontakt und Domainbindung pruefen
4. lokale Payment-Confirmation fuer `PayPal Business` vorbereiten
5. lokale Invoice-Confirmation vorbereiten
6. Invoice- und Payment-Bestaetigung ausserhalb des Workspace abwarten
7. License-Issuance-Prep referenzieren
8. Signed-Delivery-Prep referenzieren
9. Protected Customer Install Pack referenzieren
10. Customer-Release-Authorization lokal vorbereiten
11. Protected Customer Release Decision lokal vorbereiten
12. reale Customer-Release weiter `approval_required` halten

## Grenzen

- keine echte Zahlung im Workspace
- keine echte Rechnungsausgabe im Workspace
- keine offene Delivery
- keine Customer-Login-Funktion

## Status

- Orchestrierung: `blueprint_ready`
- reale Kauf-zu-Freigabe-Kette: `approval_required`
