# Operator Minimal Input List

## Zweck

Diese Liste enthaelt nur die minimal noetigen Betreiberangaben fuer Pilot Candidate 1 und 2. Keine Secrets in Klartext hier eintragen.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es sammelt nur Inputs fuer spaetere, freigabepflichtige Schritte.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Die Liste selbst nicht. Die spaeteren Piloten ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ohne Anwendung bleibt der Rueckweg Nicht-Freigabe.

## Gemeinsame Minimalangaben

- freigegebene Cloudflare-Zone
- bestaetigte Domain und Homepage-Pfad
- erlaubter Connector-Typ: `Cloudflare`
- bestaetigter Minimalzugang vorhanden: `ja / nein`
- Secret-Uebergabepfad ausserhalb dieser Dokumente definiert: `ja / nein`
- benannte Pilot-Verantwortung
- benannte Rollback-Verantwortung
- bestaetigte Validierungsfenster: `Sofortcheck / 1d / 7d`

## Zusaetzlich fuer Pilot 1

- erlaubte Regeltypen fuer HTML-Kompression
- ausgeschlossene Pfade
- ausgeschlossene Cookie-, Session- und Login-Faelle
- Bestaetigung, dass nur textbasierte Homepage-HTML-Responses betroffen sein duerfen

## Zusaetzlich fuer Pilot 2

- erlaubte Cache-Regeltypen
- ausgeschlossene Pfade
- ausgeschlossene Cookie-, Session-, Login-, Preview- und Admin-Faelle
- Bestaetigung, dass nur anonyme Homepage-Requests betroffen sein duerfen
- Bestaetigung, welche Bypass-Logik erlaubt ist

## Was nicht hier hinein gehoert

- API-Token im Klartext
- Passwoerter
- breit gefasste Rechte ohne Scope
- Freigaben fuer globale oder siteweite Regeln
