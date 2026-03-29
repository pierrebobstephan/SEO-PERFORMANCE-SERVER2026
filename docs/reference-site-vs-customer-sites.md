# Reference Site vs Customer Sites

## Zweck

Dieses Dokument trennt das Referenzsystem von spaeteren Kunden-Websites.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es trennt Zielsysteme und verhindert implizite Uebertragung von Rechten.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede spaetere echte Domain-Anwendung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Jedes Zielsystem behaelt seinen eigenen Rueckweg.

## Referenzsystem

`electri-c-ity-studios-24-7.com` ist:

- Referenzsystem
- Lern- und Testinstanz
- Quelle fuer erste Produkt-Heuristiken
- nicht automatisch Vorlage fuer globale Kundenwirkung

## Kunden-Websites

Spaetere Kunden-Websites sind:

- getrennte Zielsysteme
- lizenzgebunden
- scopegebunden
- policygebunden
- konfliktbehaftet in je eigener Theme-, Builder- und SEO-Plugin-Lage

## Was nicht uebertragen werden darf

- keine automatische Freigabe aus dem Referenzsystem
- keine automatische Policy-Uebernahme ohne Domain-Pruefung
- keine automatische Theme- oder Builder-Annahme
- keine automatische globale Optimierungswirkung

## Was uebertragen werden darf

- defensive Heuristiken
- Validierungslogik
- Rollback-Muster
- produktseitige Sicherheitsregeln

## Status

- Referenzsystem: `observe_only` fuer reale Wirkung
- Kunden-Websites: `blueprint_ready`
- echte Kundenwirkung: `approval_required`
