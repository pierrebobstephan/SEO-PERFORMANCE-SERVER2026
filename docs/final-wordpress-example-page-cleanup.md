# Final WordPress Example Page Cleanup

## Ziel

Die Beispiel-Seite soll als Scope-V1-Testseite erhalten bleiben, darf aber keine `localhost`-Reste oder irrefuehrenden Dashboard-Links mehr tragen.

## Betroffene Stelle

- page url: `https://wp.electri-c-ity-studios-24-7.com/wordpress/beispiel-seite/`
- current issue: der Hinweis `dein Dashboard` verweist noch auf `localhost`

## Bevorzugter minimaler Fix

1. Seite im WordPress-Editor oeffnen.
2. nur den Standard-WordPress-Onboarding-Abschnitt mit Dashboard-Link anpassen oder entfernen.
3. restlichen Seiteninhalt unveraendert lassen, solange kein weiterer `localhost`-Rest sichtbar ist.

## Erlaubte Zielvarianten

- Dashboard-Hinweis auf `https://wp.electri-c-ity-studios-24-7.com/wordpress/wp-admin/` umstellen
- oder den gesamten Standard-Onboarding-Abschnitt loeschen

## Nicht erlaubt

- Scope der Seite fuer den Test ausweiten
- neue Marketing- oder Rechtsaussagen erfinden
- unnoetige globale Search-Replace-Schritte ohne Dry-Run und Backup

## Gate

- Example Page Cleanup: `blocked` bis der Dashboard-Hinweis keinen `localhost`-Rest mehr enthaelt
