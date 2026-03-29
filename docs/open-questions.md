# Offene Angaben fuer den Produktivbetrieb

Diese Angaben fehlen aktuell oder sind absichtlich nicht hinterlegt. Ohne sie bleibt das System im Beobachtungsmodus.

## Zielsystem

- Welche Ziel-Domain(s) und ggf. Staging-Domain(s) sollen ueberwacht werden?
- Sind HTTP-Lesezugriffe auf diese Domains aus diesem Workspace ausdruecklich erlaubt?
- Welche Verzeichnisse oder Artefakte innerhalb des freigegebenen Workspace gelten als legitime Zielbereiche?

## Eingriffstiefe

- Sind ausschliesslich Analyse und Reporting erlaubt?
- Sind spaeter vorbereitete Patch-Plaene fuer das externe WordPress-System erlaubt?
- Gibt es klar freigegebene Write-Zielbereiche fuer sichere Automatisierung?

## Reporting und Alerting

- Wer soll Reports erhalten?
- Welche Berichtsformen sind gewuenscht: Kurzreport, Incident-Report, Trendreport, Wochenreport, Monatsreport?
- Welche Kanaele sind erlaubt: SMTP, Mail-Relay, Webhook, Chat, keine aktiven Benachrichtigungen?

## Zugangsdaten und APIs

- SMTP-Host, Port, Username, Passwort, Absender, Empfaenger
- API-Zugaenge fuer Search Console, Analytics, CDN, Monitoring oder andere Datenquellen

## Betriebsparameter

- gewuenschte Pruefintervalle
- Performance-Schwellenwerte
- bevorzugte SEO-Prioritaeten
- Eskalationslogik fuer kritische Befunde

