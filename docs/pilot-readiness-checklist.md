# Pilot Readiness Checklist

## Zweck

Diese Checkliste prueft vor jedem spaeteren Pilot, ob die bindende Doktrin aus [AGENTS.md](/opt/electri-city-ops/AGENTS.md), [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md) und [doctrine-alignment-report.md](/opt/electri-city-ops/docs/doctrine-alignment-report.md) eingehalten wird.

## Doktrinischer Pflichtcheck

- Ist der geplante Schritt mit [AGENTS.md](/opt/electri-city-ops/AGENTS.md) konsistent?
- Ist der geplante Schritt mit [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md) konsistent?
- Ist der geplante Schritt mit [doctrine-alignment-report.md](/opt/electri-city-ops/docs/doctrine-alignment-report.md) konsistent oder schliesst er dokumentierte Luecken defensiv?
- Bleibt `observe_only` aktiv, solange Inputs oder Freigaben fehlen?
- Gibt es keinerlei Wirkung ausserhalb `/opt/electri-city-ops`, solange kein Pilot freigegeben ist?
- Ist Rocket Cloud vollstaendig unangetastet?

## Gate-Check

- Ist ein klarer Connector-Typ festgelegt?
- Ist der Ziel-Scope klein und eindeutig?
- Ist der aktuelle Gate-Status dokumentiert?
- Wuerde der Schritt bei Unsicherheit auf `observe_only`, `approval_required` oder `blocked` fallen?

## Daten-Check

- Gibt es ausreichend Observe-only-Historie?
- Sind die Ursachenannahmen plausibel und nicht nur auf einem Einzelsample aufgebaut?
- Sind Primaermetriken und Nachbarsignale definiert?
- Sind 1d-, 7d- und falls noetig 30d-Fenster vorbereitet?

## Sicherheits-Check

- Ist der Blast Radius klein?
- Ist der Rueckweg klar und dokumentiert?
- Sind keine OS-, Service-, Scheduler- oder Fremdsystemeingriffe beteiligt?
- Sind keine globalen oder unklar begrenzten Regeln vorgesehen?

## Freigabe-Check

- Liegen alle verbindlichen Betreiberfreigaben vor?
- Liegt Connector-Freigabe vor?
- Liegt Zielbereichs-Freigabe vor?
- Liegt Pilot-Scope-Freigabe vor?
- Liegt Rollback-Verantwortung vor?

## Secret-Check

- Sind die minimal notwendigen Zugangsdaten vorhanden?
- Sind die Zugangsdaten scope-begrenzt?
- Sind nicht benoetigte Rechte explizit ausgeschlossen?

## Validation-Check

- Existiert eine Vorher-Messung?
- Existiert ein Validierungsobjekt mit Primaermetriken?
- Existieren Nachbarsignale?
- Sind Abort- und Rollback-Kriterien definiert?

## Simulations- und Adaptions-Check

- Ist vor jeder spaeteren Anwendung ein expliziter `simulate`-Schritt dokumentiert?
- Ist beschrieben, welche Nachbarsignale im Simulations- oder Smoke-Check geprueft werden?
- Ist festgelegt, wann ein Schritt auf `approval_required` zurueckfaellt, wenn Signale gemischt oder unklar sind?
- Ist festgelegt, wann ein Schritt als `blocked` endet, weil Scope, Risiko oder Kausalitaet doktrinisch nicht tragfaehig sind?
- Ist ein `adapt`-Pfad beschrieben, der nur Planung, nicht aber ungedeckte Anwendung erweitert?

## Ergebnislogik

Setze `pilot_ready` nur wenn alle Pflichtchecks positiv beantwortet sind.

Setze `approval_required` wenn:

- Freigaben fehlen
- Secrets fehlen
- Connector oder Zielbereich noch nicht bestaetigt sind
- der Schritt doktrinisch grundsaetzlich moeglich ist, aber Simulations-, Validierungs- oder Verantwortungsdaten fehlen

Setze `blocked` wenn:

- kein klarer Rollback existiert
- der Blast Radius zu gross ist
- der Zielscope unklar ist
- die Massnahme gegen [AGENTS.md](/opt/electri-city-ops/AGENTS.md), [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md) oder [doctrine-alignment-report.md](/opt/electri-city-ops/docs/doctrine-alignment-report.md) verstoesst
- ein benoetigter Simulations- oder Adaptionspfad nicht sauber definierbar ist

## Aktueller Stand fuer Pilot Candidate 1

Aktuelle Bewertung:

- nicht `pilot_ready`
- aktuell `approval_required`

Fehlende Punkte:

- Cloudflare-Zone
- minimaler Connector-Zugang
- Zustimmung zu spaeterer Edge-Regelung
- dokumentierte Session- und Cookie-Ausnahmen
- verbindliche Rollback-Verantwortung
- dokumentierter Simulationspfad vor jeder spaeteren Anwendung
