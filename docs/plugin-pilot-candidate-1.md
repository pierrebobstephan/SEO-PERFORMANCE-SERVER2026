# Plugin Pilot Candidate 1

## Titel

Homepage-Meta-Description ueber einen WordPress-Plugin-Pfad kontrolliert verbessern

## Strategy Status

- Connector-Pfad: `WordPress plugin primary path`
- aktueller Gate-Status: `approval_required`
- keine Anwendung ohne weitere Betreiberinputs, Scope-Klaerung, Validierung und Rollback

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es ist nur ein lokaler Blueprint fuer einen spaeteren Plugin-Piloten.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Ja fuer jede spaetere Plugin-Anwendung.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Rueckkehr zur vorherigen Description-Quelle oder zum dokumentierten Vorwert.

## Ziel

Die Homepage-Description soll spaeter ueber einen klar begrenzten Plugin-Pfad verbessert werden, ohne doppelte oder widerspruechliche Meta-Ausgabe zu erzeugen.

## Beobachtungsgrundlage

- aktuelle Meta Description: `Global Electro Music Online Radio 24 / 7`
- aktuelle Laenge: `40`
- Homepage-Status stabil `200`

## Vermutete Ursache

Description-Logik liegt in Theme, Builder oder SEO-Plugin zu knapp oder uneinheitlich vor.

## Warum dies der erste Plugin-Pilot sein sollte

- enger Homepage-Scope
- gut messbare Wirkung
- geringeres Risiko als HTML-/Markup-Reduktion
- meist sauberer rueckrollbar als strukturelle Template-Eingriffe

## Spaeterer Ziel-Connector

- `WordPress plugin`

## Geplanter Scope fuer einen spaeteren Pilot

- nur Homepage
- nur Meta-Description-Quelle
- keine siteweiten Massnahmen
- keine gleichzeitige Aenderung von Title, Canonical oder Robots ohne eigene Freigabe

## Erforderliche Inputs

- welches SEO-Plugin, Theme oder welcher Builder aktuell die Description steuert
- freigegebener Homepage-Scope
- inhaltliche Betreiberfreigabe fuer die neue Description
- definierte Rollback-Verantwortung
- definierte Validierungsfenster

## Risiken

- doppelte Meta-Description-Ausgabe
- Konflikt zwischen Plugin-, Theme- und SEO-Plugin-Quelle
- inhaltlich schwache oder inkonsistente Description

## Simulationspfad vor spaeterer Anwendung

- aktuelle Description-Quelle lokalisieren
- pruefen, ob bereits SEO-Plugin-Filter aktiv sind
- Ziel-Description und Rueckfallpfad dokumentieren
- Validierungsobjekt vorab definieren

## Validierung

Primaermetriken:

- `meta_description_length` bewegt sich in sinnvollen Zielbereich
- Homepage liefert genau eine fachlich passende Description

Nachbarsignale:

- Title, Canonical und Robots bleiben stabil
- keine doppelte Meta-Ausgabe
- keine neue HTML-Regression

Zeitfenster:

- Sofortcheck
- 1d
- 7d

## Rollback

- Rueckkehr zur vorherigen Description-Quelle oder zum dokumentierten Vorwert
- Sofortpruefung auf eindeutige Meta-Ausgabe
- 1d-Nachbeobachtung

## Weg von approval_required zu pilot_ready

1. Description-Quelle in WordPress eindeutig klaeren.
2. Minimalen Plugin-Scope fuer nur die Homepage bestaetigen.
3. Betreiberfreigabe fuer Inhalt und Scope erteilen.
4. Validierungs- und Rollback-Verantwortung bestaetigen.

## Ergebnis

Dieser Plugin-Pilot ist als doctrine-konformer erster WordPress-Blueprint vorbereitet, bleibt aber bis zu den fehlenden Inputs und Freigaben im Status `approval_required`.
