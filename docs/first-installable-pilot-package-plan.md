# First Installable Pilot Package Plan

## Ziel

Ein erstes technisch installierbares, aber streng begrenztes Pilotpaket wird nur fuer staging/test vorbereitet.

## Paketprofil

- staging-only
- `pilot` channel
- `safe_mode` / `observe_only` first
- enger Diagnostics- und Validation-Scope
- keine offene Multi-Domain-Wirkung

## Auslieferungsgrenzen

- keine oeffentliche Download-Ausgabe
- keine Customer-Self-Service-Installation
- keine Freigabe ohne Domain-, Scope-, Backup- und Rollback-Klarheit

## Gate

- First Installable Pilot Package: `approval_required`
