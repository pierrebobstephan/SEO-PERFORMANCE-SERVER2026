# Operator Customer Onboarding Runbook

## Zweck

Dieses Runbook beschreibt den spaeteren lokalen Operator-Pfad fuer Kunden-Onboarding.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es trennt Referenz- und Kunden-Domain strikt.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Runbook nicht. Reale Kundenanbindung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Fehlende Inputs fuehren auf `approval_required` oder `blocked`.

## Lokale Schritte

1. Domain und Rolle erfassen
2. CMS als WordPress bestaetigen
3. Scope und Channel festlegen
4. Konfliktlage und Source-Mapping-Status dokumentieren
5. Onboarding-Eintrag lokal validieren
6. Dry-Run durchfuehren

## Status

- Customer-Onboarding-Runbook: `blueprint_ready`
- reale Kundenanbindung: `approval_required`
