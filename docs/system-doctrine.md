# System Doctrine

## Status

Dieses Dokument ist die kanonische Langfassung der Systemdoktrin. [AGENTS.md](/opt/electri-city-ops/AGENTS.md) ist die knappe, verbindliche Repo-Steuerdatei und verweist auf diese Langfassung.

## Kanonische Kerndoktrin

"Das Programm soll vollstaendig autonom, robust und defensiv-schuetzend arbeiten, dauerhaft aus seinen Daten lernen und sich selbst optimieren. Es verbessert Performance, Struktur und Ressourcennutzung kontinuierlich, erkennt Fehler automatisch und korrigiert sie eigenstaendig. Alle internen Module arbeiten harmonisch zusammen und tauschen Wissen aus. Selbstverbesserungen am Code erfolgen ausschliesslich sicher, validiert und ohne Risiko fuer das Betriebssystem. Ziel ist ein stabiles, lernfaehiges und selbstheilendes System, das sich langfristig weiterentwickelt."

## Zielbild des autonomen, lernfaehigen, selbstheilenden Systems

Das System ist als langfristig betriebener SEO-, Performance- und Stabilitaets-Operations-Stack gedacht. Es soll:

- dauerhaft Zustand, Trends, Fehlerbilder und Ressourcensignale beobachten
- Erkenntnisse aus Historie und Validierung in bessere Priorisierung und Planung uebersetzen
- spaeter kontrollierte Optimierungen vorbereiten und nur innerhalb klarer Sicherheitsgrenzen anwenden
- Fehlschlaege erkennen, Folgen begrenzen und ueber Rollback sowie Lernen in robustere Folgeentscheidungen uebersetzen

Autonomie bedeutet in dieser Doktrin nicht grenzenlose Selbsttaetigkeit, sondern selbststaendige Arbeit innerhalb harter Schutzlogik.

## Defensive Schutzlogik

Defensive Schutzlogik hat Vorrang vor Optimierungsgeschwindigkeit.

- Im Zweifel gilt Beobachtung vor Eingriff.
- Bei Unsicherheit, Datenluecken, fehlenden Zugangsdaten oder fehlenden Freigaben bleibt das System in `observe_only`.
- Kein Modul darf seine Wirkungskette an Guardrails, Gate-Logik, Validierung oder Rollback vorbei fuehren.
- Kein Optimierungsziel darf Risiken fuer Betriebssystem, Rocket Cloud, nicht freigegebene Fremdsysteme oder unklare produktive Seiteneffekte rechtfertigen.

Diese Doktrin ist mit der vorhandenen approval-, validation- und rollback-Logik gekoppelt und darf von spaeteren Connectoren nicht abgeschwaecht werden.

## Leitprinzip und bindender Kernzyklus

Das System folgt dem Leitprinzip:

`so autonom wie moeglich, so defensiv wie noetig, so sicher wie zwingend`

Jede systemische Verbesserung folgt dem Kernzyklus:

`observe -> analyze -> decide -> simulate -> apply -> validate -> learn -> adapt -> document`

Zwingende Folgerungen:

- ohne Beobachtung keine Entscheidung
- ohne Simulation keine Anwendung
- ohne Validierung kein Erfolg
- ohne Rueckweg keine Freigabe

## Schutzhierarchie

Bei Zielkonflikten gilt diese Prioritaet:

1. Sicherheit des Betriebssystems
2. Stabilitaet und Erreichbarkeit des Gesamtsystems
3. Integritaet von Daten, Konfiguration und Zustandsmodellen
4. Korrektheit und Validitaet der Funktion
5. defensive Fehlerminimierung
6. Performance und Ressourceneffizienz
7. Komfort, Tempo und Erweiterung

Performance-Gewinne duerfen niemals Stabilitaet, Sicherheit oder Integritaet opfern.

## Modulkooperation und Wissensaustausch

Alle internen Module muessen harmonisch zusammenarbeiten und Wissen austauschen. Kein Modul ist als isolierter Optimierer gedacht.

Mindestens folgende Wissensfluesse sind dauerhaft vorgesehen:

- Observe-only Audits liefern Rohsignale an trend_engine, learning_engine und reporting_engine.
- trend_engine liefert Drift-, Stabilitaets- und Vertrauenssignale an change_planner und approval_gate.
- learning_engine liefert Wiederholungsmuster, Risikoerfahrungen und Erfolgswahrscheinlichkeiten an Priorisierung, Validierung und Rollback-Bewertung.
- validation_engine und rollback-Logik liefern Rueckmeldungen ueber Erfolg, Misserfolg und Nebenwirkungen an learning_engine.
- reporting_engine macht Rohdaten, Entscheidungen, Gates und Begruendungen fuer Operatoren nachvollziehbar.

Harmonie bedeutet dabei:

- gemeinsame Datenmodelle statt isolierter Sonderlogiken
- erklaerbare Uebergaenge zwischen Beobachtung, Planung, Freigabe, Anwendung, Validierung und Lernen
- keine stillen Seiteneffekte einzelner Module

## Kontinuierliches Lernen aus Historie, Trends, Fehlern, Erfolgen und Rollbacks

Lernen ist nicht optional, sondern Bestandteil der Systemidentitaet.

Das System soll dauerhaft lernen aus:

- historischen Messwerten
- Trendfenstern wie 1d, 7d, 30d und 365d
- wiederkehrenden Fehlerbildern
- erfolgreichen Optimierungen
- fehlgeschlagenen Massnahmen
- Rollback-Ausloesern und Rollback-Ergebnissen

Lernen darf jedoch nicht unkontrolliert sein.

- Kleine oder verrauschte Datenmengen duerfen nicht zu aggressiven Schlussfolgerungen fuehren.
- Wiederholung erhoeht Gewicht, ersetzt aber keine kausale Plausibilitaet.
- Eine Heuristik, die wiederholt zu schlechten Entscheidungen fuehrt, muss spaeter durch die learning_engine herabgestuft oder blockiert werden.

## Sichere Selbstoptimierung

Selbstverbesserung des eigenen Codes ist erlaubt, aber nur unter denselben oder strengeren Schutzregeln wie spaetere externe Optimierung.

Verbindliche Bedingungen:

- nur innerhalb `/opt/electri-city-ops`
- keine Wirkung auf Betriebssystem, Rocket Cloud oder nicht freigegebene Fremdsysteme
- dokumentierte Begruendung
- lokale Tests
- Validierung des erwarteten Ergebnisses
- klarer Rollback-Pfad
- keine unvalidierte Selbstmodifikation

Selbstoptimierung darf niemals die Guardrails, die Observability oder die Ruecknehmbarkeit des Systems schwaechen.

## Zulaessige Autonomie, Selbstheilung und Code-Selbstverbesserung

Das System darf selbststaendig:

- Messdaten erfassen und korrelieren
- Muster, Anomalien und Engpaesse erkennen
- Hypothesen bilden und bewerten
- bekannte sichere Korrekturen lokal anwenden
- Validierungen automatisiert wiederholen
- Optimierungen priorisieren
- Rollbacks automatisch ausloesen
- interne Regeln verbessern, wenn diese Verbesserung selbst validiert wurde

Das System darf nicht selbststaendig:

- Rechte ausweiten
- unfreigegebene Connectoren aktivieren
- globale oder mehrdeutige Regeln produktiv schalten
- OS-kritische Bereiche veraendern
- Fremdsysteme ohne Freigabe und minimalen Scope veraendern
- unvalidierte Selbstverbesserungen live schalten
- unklare Ursachen mit aggressiven Massnahmen erraten

Automatische Selbstheilung ist nur zulaessig, wenn:

- die Ursache mit hoher Plausibilitaet bekannt ist
- die Massnahme lokal begrenzt ist
- sie dokumentiert und reversibel ist
- weder OS-Schutz noch unfreigegebene Fremdsysteme beruehrt werden
- der Blast Radius klein und bekannt ist
- Erfolg und Fehlschlag kurzfristig validierbar sind

## Harte Grenzen gegen Risiken fuer Betriebssystem und Fremdsysteme

Folgende Grenzen sind nicht verhandelbar:

- keine Aenderungen ausserhalb `/opt/electri-city-ops`
- keine Aenderungen an Rocket Cloud
- keine externen Schreibzugriffe ohne ausdrueckliche Freigabe
- keine Aktivierung von systemd, cron, Benachrichtigungen oder Connectoren ohne Freigabe
- keine Cloudflare- oder WordPress-Aenderungen ohne freigegebenen Connector, Gate-Status, Validierung und Rollback
- keine OS-, Kernel-, Paket-, Firewall- oder Service-Manipulationen

Betriebssystemschutz hat immer Vorrang. Wenn Autonomie und Systemsicherheit in Konflikt stehen, gewinnt die Sicherheit.

## Connector- und Secret-Doktrin

Kein externer Eingriff ohne:

- klaren Connector
- minimalen Scope
- bindende Freigabe
- minimal notwendige Rechte
- dokumentierten Zielbereich

Es gilt:

- keine impliziten Workarounds
- keine breit gefassten Tokens
- keine Nutzung ungepruefter Secrets
- keine reale Wirkung ohne freigegebenen Zielraum

Fehlende Secrets oder Freigaben werden niemals durch Annahmen kompensiert. In solchen Faellen bleibt das System in `observe_only`, `blueprint_ready` oder `approval_required`.

## Scope-Disziplin und Blast-Radius-Prinzip

Jede Massnahme braucht einen exakt definierten Zielbereich.

Ein gueltiger Scope ist:

- klein
- eindeutig
- fachlich begruendet
- technisch abgrenzbar
- messbar
- rueckrollbar

Ungueltig sind Massnahmen mit:

- globaler oder diffuser Wirkung
- unklaren Regelketten
- nicht dokumentierten Ausnahmen
- nicht abschaetzbaren Seiteneffekten
- unbestimmtem Zielsystem

Vor realer Anwendung muss beantwortet sein:

- was genau wird beruehrt
- was darf unter keinen Umstaenden beruehrt werden
- wie weit ein Fehler wirken kann
- wie schnell er erkannt wird
- wie schnell rueckgerollt werden kann

## Trennung von Beobachtung, Planung, Freigabe, Anwendung, Validierung und Lernen

Die Phasen duerfen logisch nicht ineinander fallen.

### Beobachtung

- nur lesen
- nur messen
- nur historisieren

### Planung

- Ursachenannahmen formulieren
- Risiken, Scope und Ziel-Connector festlegen
- Erfolgskriterien und Rollback vordenken

### Freigabe

- prueft, ob die Massnahme ueberhaupt ausserhalb des Workspace wirken darf
- ordnet die Massnahme einem Gate-Status zu

### Anwendung

- darf spaeter nur ueber freigegebene Connectoren und nur mit kleinem, klar begrenztem Scope erfolgen

### Validierung

- vergleicht Vorher und Nachher
- bewertet Primaermetriken und Nachbarsignale
- kann bei Bedarf `rollback_required` ausloesen

### Lernen

- speichert Ergebnisse, Fehlmuster, Erfolgswahrscheinlichkeiten und Rollback-Erfahrungen
- passt Priorisierung und Vorsicht langfristig an

## Observe-only als sicherer Default-Fallback

`observe_only` ist nicht nur ein Betriebsmodus, sondern der sicherste Rueckzugszustand des Systems.

Er gilt insbesondere bei:

- fehlenden Ziel-Inputs
- fehlenden Zugangsdaten
- fehlender Connector-Freigabe
- unklarer Kausalitaet
- instabiler Datenlage
- hohem Blast Radius

Observe-only ist damit nicht ein "reduzierter Modus", sondern die fundamentale Sicherheitsbasis des Gesamtsystems.

## Erweiterte Betriebs- und Gate-Zustaende

Neben `observe_only` sind langfristig folgende Zustandsklassen doktrinisch sinnvoll:

- `local_safe_self_heal`
- `blueprint_ready`
- `approval_required`
- `pilot_ready`
- `active_pilot`
- `stable_applied`
- `degraded_safe`
- `blocked`
- `rollback_required`

Diese Zustaende duerfen jedoch nur ueber Gate-, Validation- und Rollback-Logik erreicht werden, niemals durch implizite Modulentscheidungen.

## Unsicherheitsdoktrin

Unsicherheit ist ein Signal fuer Vorsicht.

Bei hoher Unsicherheit muss das System:

- im Beobachtungsmodus bleiben
- weitere Evidenz sammeln
- den Scope verkleinern
- den Vertrauensgrad kennzeichnen
- auf klarere Daten oder Freigaben warten

Unklarheit darf niemals durch aggressive Aenderungen kompensiert werden.

## Dokumentationspflicht

Jede relevante Beobachtung, Entscheidung, Aenderung, Validierung, Rueckrollung und gelernte Regel muss nachvollziehbar dokumentiert werden.

Mindestens zu erfassen sind:

- Kontext
- Ziel
- Scope
- Ausgangszustand
- Hypothese
- Eingriff
- Ergebnis
- Nebeneffekte
- Rollback-Pfad
- Lerneffekt
- finaler Status

Ein nicht dokumentierter Eingriff gilt doktrinisch als unvollstaendig.

## Erfolgskriterien

Das System erfuellt diese Doktrin nur dann, wenn es nachweisbar:

- stabil bleibt
- defensiv handelt
- aus Daten lernt
- bekannte Fehler sicher selbst behebt
- Optimierungen valide und kontrolliert umsetzt
- seine Module koordiniert zusammenarbeiten laesst
- sich nur innerhalb sicherer Grenzen selbst verbessert
- kritische oder fremde Bereiche nicht unbeabsichtigt beruehrt

## Verbindlichkeit fuer spaetere Connectoren und Module

Besonders streng an diese Doktrin gebunden sind spaeter:

- approval_gate
- validation_engine
- rollback-Mechanik
- learning_engine
- change_planner
- alle Cloudflare- und WordPress-Connectoren

Diese Komponenten duerfen nie zugunsten von Bequemlichkeit, Geschwindigkeit oder impliziter Annahmen abgeschwaecht werden.

## Doktrinische Schlussfolgerung

Das System darf langfristig autonomer, lernfaehiger und aktiver werden, aber nur wenn diese Autonomie:

- innerhalb harter Guardrails bleibt
- durch Historie und Trenddaten gedeckt ist
- durch Freigabe kontrolliert ist
- durch Validierung beweisbar ist
- durch Rollback sofort begrenzbar bleibt

Damit ist die oberste Systemdoktrin erfuellt: ein stabiles, lernfaehiges, selbstheilendes und langfristig evolvierendes System, das seine Schutzgrenzen nie verletzt.
