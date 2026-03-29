# Cloudflare Connector Blueprint

## Zielbereich

Der spaetere Cloudflare-Connector ist fuer Edge-nahe Optimierungen vorgesehen, vor allem:

- HTML-Kompression
- Cache-Regeln fuer anonyme Homepage-Aufrufe
- Edge-Verhalten fuer klar freigegebene oeffentliche Routen
- spaeter begrenzte Header-Regeln, sofern sie fachlich und technisch abgesichert sind

Nicht Ziel dieses Connectors:

- globale oder unklare Regelmanipulation
- sicherheitskritische Firewall- oder WAF-Aenderungen
- ungepruefte Regeln mit grossem Blast Radius

## Erlaubte spaetere Regeltypen

Die spaeter erlaubten Regeltypen sollen eng begrenzt bleiben.

### Priority Tier A

- Kompression fuer textbasierte Responses
- Cache-Regeln fuer anonyme Homepage-Requests
- Edge-TTL oder Bypass-Regeln fuer klar definierte Pfade

### Priority Tier B

- Header-Ergaenzungen fuer klar definierte Responses
- feinere Cache-Ausnahmen nach Cookie- oder Pfadlogik

### Ausgeschlossen bis zu einer Sonderfreigabe

- globale WAF-Aenderungen
- DNS-Aenderungen
- Load-Balancing-Aenderungen
- Redirect-Massenregeln
- komplexe Worker- oder Transform-Logik ohne eigene Validierungsstrecke

## Benoetigte Inputs und Freigaben

### Zuerst erforderlich

- freigegebene Cloudflare-Zone
- erlaubte Regeltypen
- Bestaetigung, dass Edge-Regeln fuer die Ziel-Domain ueberhaupt veraendert werden duerfen

### Vor spaeterer Pilotanwendung erforderlich

- Connector-Zugangsdaten oder API-Token mit eng begrenztem Scope
- Bestaetigung der betroffenen Pfade
- Bestaetigung, ob Session-, Cookie- oder Login-Pfade ausgespart werden muessen
- definierte Rollback-Fenster

## Risiken

- falsches Caching dynamischer Inhalte
- Stale-Content fuer eingeloggte oder personalisierte Nutzer
- ungewollte Interaktion zwischen Cache- und Kompressionsregeln
- zu grosser Blast Radius bei globalen Regeln

## Validierung

Jede spaetere Cloudflare-Massnahme braucht mindestens:

- Vorher-Messung fuer `Content-Encoding`, `Cache-Control`, `response_ms` und `homepage_status_code`
- Sofortcheck direkt nach der Aenderung
- 1d-Vergleich
- 7d-Vergleich
- bei relevanten Drift- oder Traffic-Aenderungen optional 30d-Vergleich

Nachbarsignale:

- Statuscode bleibt stabil
- Canonical, Title und HTML-Struktur bleiben erreichbar
- kein Anstieg von Fehlern oder ungueltigen Responses

## Rollback-Prinzip

- jede Regel braucht eine eindeutige Ruecknahmeoperation
- globale oder ueberschreibende Regelketten sind ohne saubere Vorzustandsdokumentation unzulaessig
- bei Anzeichen fuer fehlerhafte Personalisierung oder Cache-Verfremdung sofort `rollback_required`
- Ruecknahme muss dieselben Pfade und denselben Scope nutzen wie die Ausgangsregel

## Connector-Zustandsmodell

- `observe_only`
- `blueprint_ready`
- `approval_required`
- `pilot_ready`
- `blocked`
- `rollback_required`

## Freigabepflichtige Sonderfaelle

- Regeln auf mehreren Pfaden gleichzeitig
- Regeln mit Cookie- oder Session-Abhaengigkeit
- Regeln, die globale Edge-Policies ueberschreiben
- Eingriffe, die nicht mit einem klaren Vorher/Nachher-Vergleich messbar sind

