# Operator Approval Template: Cloudflare Pilot 2

## Status

- aktueller Gate-Status: `approval_required`
- Strategiestatus: `Cloudflare secondary path`
- Zweck: reine Freigabe- und Inputsammlung
- keine externe Wirkung

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es ist nur eine lokale Freigabevorlage fuer spaetere Entscheidungen.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Die Vorlage selbst nicht. Der spaetere Pilot ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ohne Anwendung ist der Rueckweg Nicht-Freigabe oder Ruecknahme vor Aktivierung.

## Referenzen

- [pilot-candidate-2.md](/opt/electri-city-ops/docs/pilot-candidate-2.md)
- [AGENTS.md](/opt/electri-city-ops/AGENTS.md)
- [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md)

## Operator-Freigabe

- Betreibername: `__`
- Datum: `__`
- Domain: `electri-c-ity-studios-24-7.com`
- Cloudflare-Zone freigegeben: `ja / nein`
- Erlaubte Cache-Regeltypen fuer diesen Pilot: `__`
- Freigegebener Scope:
  nur anonyme Homepage-Requests auf `__`
- Ausgeschlossene Pfade:
  `__`
- Ausgeschlossene Cookies, Sessions, Login-, Preview- und Admin-Faelle:
  `__`
- Bypass- oder Ausnahme-Logik ausdruecklich erlaubt:
  `ja / nein`
- Minimaler Connector-Zugang vorbereitet:
  `ja / nein`
- Secret wird separat sicher uebergeben, nicht in diesem Dokument:
  `ja / nein`
- Validierungsfenster bestaetigt:
  `Sofortcheck / 1d / 7d / optional 30d`
- Rollback-Verantwortung bestaetigt:
  `Name / Team / nein`
- Pilotentscheidung:
  `freigegeben / nicht freigegeben / rueckgestellt`
- Begruendung:
  `__`

## Pflichtbestaetigungen

- keine globale Cache-Regel
- keine Wirkung auf personalisierte, eingeloggte oder Preview-Responses
- `apply -> validate -> rollback` wird spaeter eingehalten
- bei fehlenden Inputs bleibt der Status `approval_required`
