# Plugin Distribution and Update Model

## Zweck

Dieses Dokument beschreibt, wie Plugin-Download, Updates, Policies und Rollbacks spaeter fuer lizenzierte Domains verteilt werden koennen.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es beschreibt nur einen spaeteren Distributionspfad.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede spaetere Auslieferung und jeder Update- oder Policy-Push pro Domain ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Rollback-Pakete und Policy-Rueckfall sind Teil des Modells.

## Plugin-Download fuer lizenzierte Domains

Empfohlenes Modell:

- Plugin-Download nur fuer gueltige Lizenzobjekte
- Download-Anspruch ist an `bound_domain` und `license_id` gebunden
- Ausgabe erfolgt spaeter ueber einen signierten oder anderweitig kontrollierten Download-Pfad

Nicht erlaubt:

- oeffentliche anonyme Plugin-Auslieferung mit aktiver Wirkung
- ungebundene Download-Pakete mit global freigeschalteten Features

## Update-Kanaele

Empfohlene Trennung:

- `stable`
- `pilot`
- `rollback`

Jede Domain sollte nur einen explizit freigegebenen Kanal nutzen.

## Policy-Verteilung

Die Control Plane verteilt spaeter:

- freigegebene Feature-Flags
- domaingebundene Scope-Regeln
- Konflikt-Blocklisten
- Validierungsfenster
- Rollback-Profile

Policy-Verteilung bleibt domain- und lizenzgebunden.

## Update-Verteilung

Empfohlenes Pull-Modell:

- Plugin fragt spaeter kontrolliert nach freigegebenen Updates und Policies
- keine globale ungefragte Massenauslieferung ueber alle Domains

Warum Pull-first:

- kleinerer Blast Radius
- bessere Domain-Isolation
- klarere Ruecknahme je Zielsystem

## Rollback-Verteilung

Das Produktmodell sollte spaeter unterstuetzen:

- vorige Plugin-Version
- vorige Policy-Version
- vorige Freischaltlogik

Rollback muss domainbezogen ausloesbar sein, ohne andere Kunden-Domains zu beruehren.

## Status

- Distributionsmodell: `blueprint_ready`
- aktive Auslieferung: `approval_required`
