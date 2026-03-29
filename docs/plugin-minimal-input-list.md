# Plugin Minimal Input List

## Zweck

Diese Liste enthaelt die minimal noetigen Betreiberangaben fuer den primaeren WordPress-Plugin-Pfad. Keine Secrets in Klartext hier eintragen.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es sammelt nur Inputs fuer spaetere, freigabepflichtige Plugin-Schritte.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Die Liste selbst nicht. Spaetere Plugin-Anwendung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ohne Anwendung bleibt der Rueckweg Nicht-Freigabe.

## Gemeinsame Minimalangaben fuer den Plugin-Pfad

- bestaetigte Ziel-Domain und Homepage
- freigegebener Minimal-Scope: nur Homepage oder klar benannte Templates
- aktives Theme
- aktiver Builder, falls vorhanden
- aktives SEO-Plugin, falls vorhanden
- bestaetigter Aenderungspfad fuer ein spaeteres WordPress-Plugin
- benannte Pilot-Verantwortung
- benannte Rollback-Verantwortung
- bestaetigte Validierungsfenster

## Zusaetzlich fuer Plugin Pilot 1

- welche Quelle aktuell die Meta Description steuert
- inhaltliche Richtung fuer die neue Description
- Bestaetigung, dass nur die Homepage-Description betroffen sein darf

## Zusaetzlich fuer spaetere Plugin-Piloten

- welche H1 die primaere Homepage-H1 sein soll
- welche Template- oder Builder-Bereiche fuer H1 oder Struktur aenderbar sind
- welche HTML-/Markup-Bloecke als verzichtbar gelten
- ob strukturbezogene SEO-Verbesserungen nur Homepage oder weitere Templates betreffen duerfen

## Was nicht hier hinein gehoert

- WordPress-Passwoerter im Klartext
- API-Token im Klartext
- globale Freigaben ohne Scope
- unbestimmte Theme- oder Builder-Eingriffe ohne Rueckweg
