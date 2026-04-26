# Local Browser Console

## Zweck

Dieses Dokument beschreibt die lokale Browser-Konsole fuer das doctrine-enforced SEO- und Performance-System.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Die Konsole ist lokal, read-only oder local-preview-only.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Die lokale Konsole nicht. Jede spaetere oeffentliche oder externe Freigabe waere `approval_required`.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Konsole stoppen und keine Bindung ausserhalb `127.0.0.1`.

## Start

Empfohlener Startbefehl:

```bash
python3 tools/run_local_console.py --host 127.0.0.1 --port 8765
```

Alternative:

```bash
tools/open_local_console.sh
```

## Lokale URL

- `http://127.0.0.1:8765/`
- Healthcheck: `http://127.0.0.1:8765/healthz`

## SSH-Tunnel

Optional fuer lokalen Browser-Zugriff ueber SSH, ohne den Dienst oeffentlich zu binden:

```bash
ssh -L 8765:127.0.0.1:8765 <user>@<server>
```

Danach lokal im Browser:

- `http://127.0.0.1:8765/`

## Verfuegbare Ansichten

- Runtime / System Status
- Doctrine / Guardrails / current mode
- Domain-Konfiguration
- letzte Reports / `latest.md` / `latest.json`
- Product Core Status
- Plugin MVP Status
- Backend Core Status
- Packaging / Release Preview Status
- Operator Fulfillment Cockpit
- Dry-Run / Onboarding Preview
- Preview-Objekte fuer Lizenz, Domain-Binding, Policy, Rollback, Manifest, Package-Metadata und Release-Artefakt
- Preview-Objekte fuer PayPal Business, Rechnungsautomation und Webhook-Prep
- Teststatus

## Zusätzliche lokale Testaktionen

- `Build Protected Customer Install Pack`
- `Build Signed Delivery Prep`
- `Build Checkout To Issuance Orchestration`
- `Build Payment Confirmation And Customer Release`
- `Build Invoice Confirmation And Release Decision`
- `Build Subscription Lifecycle Prep`
- `Build PayPal Business And Invoice Prep`

## Status

- lokale Browser-Konsole: `blueprint_ready`
- jede externe oder oeffentliche Freigabe: `approval_required`

## V5-Doktrinbindung

Die Konsole ist nicht nur eine lokale Uebersicht, sondern eine Explainability- und Audit-Oberflaeche fuer die 8.0-Masterdoktrin. Sie soll sichtbar machen:

- warum das System im aktuellen Gate-Zustand steht
- welche Blocker offen oder geloest sind
- welche Billing-, Delivery-, Validation- und Rollback-Pfade weiter geschuetzt bleiben
