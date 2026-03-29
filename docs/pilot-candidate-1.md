# Pilot Candidate 1

## Titel

Cloudflare HTML-Kompression fuer die anonyme Homepage von `electri-c-ity-studios-24-7.com`

## Doctrine Precheck

Bindende Referenzen:

- [AGENTS.md](/opt/electri-city-ops/AGENTS.md)
- [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md)
- [doctrine-alignment-report.md](/opt/electri-city-ops/docs/doctrine-alignment-report.md)
- [approval-gate-spec.md](/opt/electri-city-ops/docs/approval-gate-spec.md)
- [validation-engine-spec.md](/opt/electri-city-ops/docs/validation-engine-spec.md)
- [rollback-playbooks.md](/opt/electri-city-ops/docs/rollback-playbooks.md)

Doktrinische Bewertung:

- externe Wirkung waere spaeter nur ueber den freigegebenen `Cloudflare`-Connector zulaessig
- `observe_only` bleibt bis zur Vollstaendigkeit aller Freigaben und Inputs aktiv
- `apply -> validate -> rollback` ist zwingend
- Betriebssystemschutz, Rocket-Cloud-Schutz und Workspace-Grenzen sind nicht beruehrbar

Gate-Status heute:

- `approval_required`

Warum nicht `pilot_ready`:

- keine Cloudflare-Zone freigegeben
- keine API-Zugangsdaten freigegeben
- keine verbindliche Zustimmung fuer spaetere Edge-Regelaenderung
- keine bestaetigten Cookie-, Session- oder Login-Ausnahmen

Warum derzeit nicht `blocked`:

- Ziel-Connector ist klar
- Beobachtungslage ist fachlich plausibel
- Rollback-Pfad ist prinzipiell formulierbar
- Blast Radius kann spaeter auf eine enge HTML-/Homepage-Regel begrenzt werden

## Ziel

Die anonyme Homepage soll spaeter komprimierte HTML-Responses ausliefern, um Transferkosten, Bandbreite und Render-Start zu verbessern.

## Beobachtungsgrundlage

Aktueller Live-Stand aus Observe-only:

- `Content-Encoding` fehlt
- `html_bytes` liegt bei `183759`
- `response_ms` stieg ueber drei Samples von `222.5` auf `225.5` auf `236.9`
- `homepage_status_code` ist stabil `200`

## Vermutete Ursache

HTML-Kompression ist am Edge oder auf der Origin-Response-Strecke nicht aktiv oder wird nicht wirksam bis zum Client durchgereicht.

## Spaeterer Ziel-Connector

- `Cloudflare`

## Geplanter Scope fuer einen spaeteren Pilot

- nur anonyme oeffentliche Homepage-Responses
- nur textbasierte HTML-Antworten
- keine Login-, Session- oder personalisierten Pfade
- keine globalen oder mehrdeutigen Regelketten

## Erforderliche Inputs

- freigegebene Cloudflare-Zone
- erlaubte Regeltypen fuer Kompression
- Bestaetigung des exakten Pilot-Scope
- Bestaetigung der ausgeschlossenen Pfade und Cookie-Faelle
- spaetere Connector-Zugangsdaten mit minimalem Scope

## Risiken

- unvollstaendige oder unwirksame Kompressionsregel
- Wechselwirkung mit spaeteren Cache-Regeln
- unerkannte Spezialfaelle bei Responses, die nicht komprimiert werden sollen

## Simulationspfad vor spaeterer Anwendung

- Header- und Response-Baseline fuer wiederholte Homepage-Requests fixieren
- pruefen, welche Response-Typen strikt ausgeschlossen bleiben muessen
- Primaermetriken und Nachbarsignale fuer Nicht-Zielpfade gegenpruefen
- erst nach dokumentiertem Simulationsergebnis von `approval_required` in Richtung `pilot_ready` bewerten

## Validierung

Primaermetriken:

- `content_encoding` vorhanden
- `homepage_status_code` bleibt `200`

Nachbarsignale:

- `response_ms` verschlechtert sich nicht unnoetig
- HTML bleibt lesbar und semantisch stabil
- keine neuen Fetch- oder Parsing-Fehler

Zeitfenster:

- Sofortcheck
- 1d
- 7d
- optional 30d, falls spaetere Wechselwirkung mit Cache-Regeln bewertet werden soll

## Rollback

- Kompressionsregel auf dokumentierten Vorzustand zuruecksetzen
- sofortige Header-, Status- und HTML-Pruefung
- 1d-Nachbeobachtung

## Adaptionspfad

- bei gemischten Signalen Rueckfall auf `approval_required`
- bei unklarer Nebenwirkung oder zu grossem Blast Radius Hochstufung auf `blocked`
- nur bei stabiler Simulations-, Freigabe- und Validierungslage spaeter `pilot_ready`

## Weg von approval_required zu pilot_ready

1. Cloudflare-Zone freigeben.
2. Erlaubte Regeltypen verbindlich bestaetigen.
3. Cookie-, Session- und Login-Ausnahmen dokumentieren.
4. API-Token oder anderen minimalen Connector-Zugang freigeben.
5. Validierungsfenster und Rollback-Verantwortung bestaetigen.

## Phase-5-Ergebnis

Dieser Pilotkandidat ist als doctrine-konformer Blueprint vorbereitet, bleibt aber bis zu den fehlenden Freigaben und Inputs im Status `approval_required`.
