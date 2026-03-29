# Pilot Candidate 2

## Titel

Cloudflare Cache-Strategie fuer anonyme Homepage-Requests von `electri-c-ity-studios-24-7.com`

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
- `observe_only` bleibt bis zur Vollstaendigkeit aller Freigaben, Inputs und Ausschlussregeln aktiv
- `apply -> validate -> rollback` ist zwingend
- Betriebssystemschutz, Rocket-Cloud-Schutz und Workspace-Grenzen sind nicht beruehrbar

Gate-Status heute:

- `approval_required`

Warum nicht `pilot_ready`:

- keine Cloudflare-Zone freigegeben
- keine API-Zugangsdaten freigegeben
- keine verbindliche Zustimmung fuer spaetere Cache-Regeln
- keine bestaetigten Cookie-, Session-, Login- und Bypass-Ausnahmen
- kein dokumentierter Simulationspfad fuer anonyme gegen personalisierte Requests

Warum derzeit nicht `blocked`:

- Ziel-Connector ist klar
- Beobachtungslage ist fachlich plausibel
- Scope kann spaeter auf eine enge Homepage-Regel begrenzt werden
- Rollback-Pfad ist prinzipiell formulierbar

## Ziel

Die anonyme Homepage soll spaeter eine kontrollierte Cache-Strategie erhalten, um wiederholte oeffentliche Requests effizienter zu bedienen, ohne personalisierte oder dynamische Antworten zu verfremden.

## Beobachtungsgrundlage

Aktueller Live-Stand aus Observe-only:

- `Cache-Control` ist `no-cache`
- `homepage_status_code` ist stabil `200`
- `response_ms` stieg ueber drei Samples von `222.5` auf `225.5` auf `236.9`
- `html_bytes` liegt stabil hoch bei `183759`

## Vermutete Ursache

Die Homepage wird derzeit entweder voll dynamisch behandelt oder mit einer bewusst sehr defensiven Cache-Policy ausgeliefert, obwohl zumindest fuer anonyme oeffentliche Requests spaeter ein engerer Cache-Scope moeglich sein koennte.

## Spaeterer Ziel-Connector

- `Cloudflare`

## Geplanter Scope fuer einen spaeteren Pilot

- nur anonyme oeffentliche Homepage-Requests
- keine Login-, Preview-, Admin-, Session- oder personalisierten Requests
- keine globalen Cache-Regeln
- keine Ausweitung auf weitere Pfade ohne eigene Freigabe

## Erforderliche Inputs

- freigegebene Cloudflare-Zone
- erlaubte Cache-Regeltypen
- Bestaetigung des exakten Homepage-Scope
- dokumentierte Cookie-, Session-, Login- und Preview-Ausnahmen
- spaetere Connector-Zugangsdaten mit minimalem Scope
- verbindliche Rollback-Verantwortung

## Risiken

- Stale-Content auf eigentlich dynamischen Antworten
- unerkannte Personalisierung ueber Cookies oder Header
- Wechselwirkung mit spaeterer Kompressionsregel
- schwierige Fehlersuche bei zu breitem Cache-Scope

## Simulationspfad vor spaeterer Anwendung

- Header- und Response-Baseline fuer wiederholte Homepage-Requests fixieren
- Ausschlusslogik fuer Login-, Cookie-, Session- und Preview-Faelle dokumentieren
- Primaermetriken und Nachbarsignale mit Nicht-Zielpfaden gegenpruefen
- erst nach dokumentiertem Simulationsergebnis von `approval_required` in Richtung `pilot_ready` bewerten

## Validierung

Primaermetriken:

- `cache_control` aendert sich wie freigegeben
- `homepage_status_code` bleibt `200`
- `response_ms` verschlechtert sich nicht

Nachbarsignale:

- HTML bleibt fuer anonyme Requests konsistent
- keine Hinweise auf falsche Personalisierung
- `canonical`, `title`, `meta_description` und `robots_meta` bleiben stabil

Zeitfenster:

- Sofortcheck
- 1d
- 7d
- optional 30d bei spaeterer Kombination mit anderen Edge-Regeln

## Rollback

- Cache-Regel auf dokumentierten Vorzustand zuruecksetzen
- sofortige Header-, Status- und HTML-Pruefung
- 1d-Nachbeobachtung

## Adaptionspfad

- bei gemischten Signalen Rueckfall auf `approval_required`
- bei unklarer Personalisierung oder zu grossem Blast Radius Hochstufung auf `blocked`
- nur bei stabiler Simulations-, Freigabe- und Validierungslage spaeter `pilot_ready`

## Weg von approval_required zu pilot_ready

1. Cloudflare-Zone freigeben.
2. Erlaubte Cache-Regeltypen verbindlich bestaetigen.
3. Cookie-, Session-, Login- und Preview-Ausnahmen dokumentieren.
4. API-Token oder anderen minimalen Connector-Zugang freigeben.
5. Simulationspfad und Rollback-Verantwortung bestaetigen.

## Phase-5-Ergebnis

Dieser Pilotkandidat ist als doctrine-konformer Blueprint vorbereitet, bleibt aber bis zu den fehlenden Freigaben, Inputs und Simulationsdaten im Status `approval_required`.
