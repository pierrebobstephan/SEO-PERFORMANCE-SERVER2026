# Commercial Chain Webhook Closure Plan

## Ziel

Die Commercial-Chain soll den PayPal-Webhook-Empfaenger nicht mehr nur als Konzept, sondern als implementierte protected Runtime-Schicht fuehren.

## Closure-Kriterien

- protected handler existiert
- Signaturverifikation existiert
- Replay-Protection existiert
- Route bleibt ausserhalb des Public Portals
- reale Aktivierung bleibt trotzdem `approval_required`

## Nach dieser Stufe weiter offen

- echte PayPal Env-Refs geladen
- reale Receiver-Verifikation im Server-Kontext
- explizite Aktivierung fuer den staging-only Realbetrieb
