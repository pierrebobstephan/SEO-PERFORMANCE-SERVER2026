# Operator License Issuance Runbook

## Zweck

Dieses Runbook beschreibt die spaetere lokale Vorbereitung einer Lizenzvergabe.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es zwingt Domain-, Scope- und Approval-Klarheit.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Runbook nicht. Reale Lizenzvergabe ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ohne Vollstaendigkeit bleibt der Status `approval_required`.

## Lokale Schritte

1. Bound-Domain bestaetigen
2. Allowed Scopes dokumentieren
3. Channel dokumentieren
4. Rollback-Profil referenzieren
5. Source-Rolle dokumentieren
6. erst dann lokalen Registry-Eintrag anlegen

## Status

- License-Issuance-Runbook: `blueprint_ready`
- reale Lizenzvergabe: `approval_required`
