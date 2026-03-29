# AGENTS.md

Diese Datei ist die knappe, verbindliche Repo-Guidance fuer Codex. Die kanonische Langfassung steht in [docs/system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md).

## Oberste Systemdoktrin

"Das Programm soll vollstaendig autonom, robust und defensiv-schuetzend arbeiten, dauerhaft aus seinen Daten lernen und sich selbst optimieren. Es verbessert Performance, Struktur und Ressourcennutzung kontinuierlich, erkennt Fehler automatisch und korrigiert sie eigenstaendig. Alle internen Module arbeiten harmonisch zusammen und tauschen Wissen aus. Selbstverbesserungen am Code erfolgen ausschliesslich sicher, validiert und ohne Risiko fuer das Betriebssystem. Ziel ist ein stabiles, lernfaehiges und selbstheilendes System, das sich langfristig weiterentwickelt."

## Verbindliche Regeln

- Die oberste Systemdoktrin ist bindend fuer jede Analyse, Planung, Dokumentation, Codeaenderung und spaetere Connector-Logik.
- `observe_only` ist der sichere Default-Fallback bei Unsicherheit, fehlenden Daten, fehlenden Freigaben oder widerspruechlichen Signalen.
- Keine Aenderungen ausserhalb `/opt/electri-city-ops`.
- Keine Aenderungen an Rocket Cloud.
- Keine externen Schreibzugriffe ohne Approval.
- Jede externe Wirkung darf spaeter nur ueber ausdruecklich freigegebene Connectoren erfolgen.
- `apply -> validate -> rollback` ist Pflicht; keine unvalidierte oder nicht ruecknehmbare Wirkung.
- Sichere Code-Selbstverbesserung ist nur innerhalb des Workspace zulaessig und nur mit Tests, Validierung, dokumentierter Begruendung und Rollback-Moeglichkeit.
- Schutz von Betriebssystem, Workspace-Grenzen und nicht freigegebenen Fremdsystemen hat immer Vorrang vor Autonomie- oder Optimierungszielen.
- [docs/system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md) ist die kanonische Langfassung und bei Detailfragen massgeblich.

## Verbindlicher Betriebszyklus

Jede relevante Handlung folgt:

`observe -> analyze -> decide -> simulate -> apply -> validate -> learn -> document`

Pflichtbestandteile:

- Scope-Definition
- Risikoklassifikation
- Validierungsdefinition
- Rollback-Planung

## Sicherheits- und Unsicherheitsregel

Wenn mehrere Optionen bestehen, ist immer zu bevorzugen:

1. kleinste sichere Aenderung
2. hoechste Evidenz
3. beste Rueckrollbarkeit
4. geringstes Seiteneffektrisiko
5. groesster Stabilitaetsgewinn
6. erst danach reiner Performancegewinn

Bei relevanter Unsicherheit gilt:

- Scope verkleinern
- mehr Evidenz sammeln
- Vertrauen absenken
- nicht anwenden
- auf `approval_required`, `blueprint_ready` oder `observe_only` zurueckfallen

## Harte Verbote

Ohne explizite und gueltige Freigabe ist verboten:

- Rechte auszuweiten
- ungepruefte oder unfreigegebene Connectoren zu aktivieren
- globale OS-, Kernel-, Firewall-, Scheduler- oder Paket-Aenderungen vorzunehmen
- Rocket Cloud zu beruehren
- fehlende Freigaben oder Secrets durch Annahmen oder Workarounds zu kompensieren
- unvalidierte Live-Selbstmodifikation durchzufuehren

## Externe Wirkung, Selbstheilung und Codeaenderung

Externe Wirkung ist nur zulaessig, wenn zugleich gilt:

- Connector ist freigegeben
- Ziel-Scope ist freigegeben
- minimale Credentials sind vorhanden
- Rollback ist dokumentiert
- Validierungsmetriken sind definiert
- Blast Radius ist klein und begrenzt

Lokale Selbstheilung ist nur zulaessig, wenn zugleich gilt:

- Ursache ist plausibel bekannt
- Wirkung ist lokal und reversibel
- Scope ist eng
- Validierung ist unmittelbar oder kurzfristig moeglich
- weder Betriebssystem noch unfreigegebene Fremdsysteme werden beruehrt

Generierter Code ist untrusted, bis Tests, Policy-Checks, Validierung und Rollback-Pfad vorliegen.

## Validierungs-, Rollback- und Dokumentationspflicht

Keine angewandte Aenderung gilt als erfolgreich ohne:

- Before-State-Evidenz
- Primaermetriken
- Nachbarsignale
- Abort-Kriterien
- Rollback-Kriterien
- Nachbeobachtungsfenster

Rollback ist verpflichtend, wenn:

- Primaermetriken kippen
- neue Fehler entstehen
- Scope verletzt wird
- Kausalitaet unklar wird
- Seiteneffekte groesser als erwartet sind

Jede relevante Handlung ist zu dokumentieren mit:

- Kontext
- Ziel
- Scope
- Hypothese
- Wirkung
- Validierung
- Seiteneffekten
- Rollback-Pfad
- finalem Status
