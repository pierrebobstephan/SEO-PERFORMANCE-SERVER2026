# Operator Checkout Review Runbook

## Zweck

Dieses Runbook beschreibt den lokalen Operator-Pfad fuer die Pruefung eines spaeteren Kauf-/Checkout-Vorgangs.

## Schritte

1. oeffentlichen Plan gegen Domain-Scope pruefen
2. gebundene Domain bestaetigen
3. Customer-Kontaktstatus pruefen
4. Payment-Methode `PayPal Business` gegen den lokalen Order-Record pruefen
5. Invoice- und Payment-Status ausserhalb des Workspace bestaetigen
6. Order-Record gegen Payment-Confirmation, Issuance-Prep, Signed-Delivery-Prep und Install-Pack abgleichen
7. Customer-Release weiter auf `approval_required` halten, bis alle realen Systeme freigegeben sind

## Abort

- Domain oder Scope unklar
- Payment oder Invoice nicht bestaetigt
- Delivery waere nicht mehr protected
- Signatur- oder Replay-Schutz-Lage unklar

## Status

- Runbook: `blueprint_ready`
- echte Kaufpruefung mit realer Wirkung: `approval_required`
