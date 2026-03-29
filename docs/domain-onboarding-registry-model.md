# Domain Onboarding Registry Model

## Zweck

Dieses Dokument beschreibt die lokale interne Onboarding-Registry fuer Referenz- und Kunden-Domains.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Onboarding bleibt domaingebunden und defensiv.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Reale Kundenanbindung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Zustandswechsel koennen auf `approval_required` oder `blocked` zurueckfallen.

## Zustaende

- `pending`
- `confirmed`
- `blocked`
- `approval_required`

## Uebergaenge

- `pending -> approval_required|confirmed|blocked`
- `approval_required -> confirmed|blocked`
- `confirmed -> approval_required|blocked`
- `blocked -> approval_required`

## Lokale Artefakte

- `schemas/domain-onboarding-entry.schema.json`
- `src/electri_city_ops/onboarding.py`

## Status

- Onboarding-Registry-Modell: `blueprint_ready`
- reale Kundenanbindung: `approval_required`
