# Customer Site Optimization Model

## Zweck

Dieses Dokument beschreibt, wie spaeter viele WordPress-Kunden-Websites ueber dieselbe Control Plane optimiert werden koennen, ohne die Doktrin zu verletzen.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es definiert domaingebundene, defensive Zielsystem-Logik.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede spaetere Kunden-Domain-Anbindung und jede aktive Aenderung pro Domain ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Jede Domain braucht eigene Validierungs- und Rollback-Pfade.

## Domain-Isolation

Jede Kunden-Domain ist ein eigenes Zielsystem mit:

- eigener Lizenz
- eigenem Scope
- eigener Policy-Zuordnung
- eigener Konfliktlage
- eigenem Validierungsverlauf
- eigenem Rollback-Pfad

Keine Kunden-Domain darf implizit von den Entscheidungen einer anderen Domain betroffen sein.

## Konflikte mit Themes, Buildern und SEO-Plugins

Das Plugin darf spaeter nicht pauschal von einer Standard-WordPress-Umgebung ausgehen.

Pro Domain sind getrennt zu bewerten:

- aktives Theme
- aktiver Builder
- aktives SEO-Plugin
- bekannte Hook- oder Template-Konflikte
- moegliche Doppel-Ausgabe

Empfohlenes Verhalten:

- Konflikt zuerst erkennen
- dann nur den freigegebenen Minimal-Scope bearbeiten
- bei Unsicherheit auf `observe_only` oder `approval_required` zurueckfallen

## Optimierungsmodell pro Domain

1. Beobachten
2. Domain-spezifische Ursachen mappen
3. Scope definieren
4. Pilot planen
5. Validierungsobjekt definieren
6. Rollback-Profil festlegen
7. erst dann spaeter domaingebunden anwenden

## Hetzner als Control Plane fuer viele WordPress-Seiten

Doctrine-konform ist das nur, wenn zugleich gilt:

- keine globale Massenwirkung
- jede reale Wirkung ist domain-, lizenz- und scopegebunden
- Policies und Rollbacks sind pro Domain getrennt
- bei Unsicherheit bleibt die Domain im nicht-anwendenden Zustand

## Status

- Kundenmodell: `blueprint_ready`
- aktive Kundenoptimierung: `approval_required`
