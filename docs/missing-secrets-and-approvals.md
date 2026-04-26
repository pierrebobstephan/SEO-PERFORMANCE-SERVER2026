# Missing Secrets and Approvals

## Zweck

Dieses Dokument listet die aktuell fehlenden Secrets, Freigaben und Zustimmungen fuer spaetere, doctrine-konforme Piloten. Solange diese Punkte offen sind, bleibt das System in `observe_only` oder stuft einzelne Blueprints auf `approval_required`.

## Sofort fehlend fuer Pilot Candidate 1

### Secrets

- kein Cloudflare-API-Token mit minimalem Scope vorhanden

### Freigaben

- keine freigegebene Cloudflare-Zone dokumentiert
- keine Zustimmung fuer spaetere HTML-Kompressionsregel dokumentiert
- keine Zustimmung fuer spaetere Cache-nahe Edge-Aenderungen dokumentiert

### Scope-Klaerungen

- keine bestaetigten Cookie-, Session- und Login-Ausnahmen
- kein verbindlich freigegebener Homepage-Pfad-Scope fuer spaetere Edge-Regeln

### Verantwortlichkeiten

- keine verbindliche Pilot-Verantwortung dokumentiert
- keine verbindliche Rollback-Verantwortung dokumentiert

## Zusaetzlich fehlend fuer Pilot Candidate 2

### Secrets

- kein Cloudflare-API-Token mit minimalem Scope vorhanden

### Freigaben

- keine Zustimmung fuer spaetere Homepage-Cache-Regel dokumentiert
- keine Zustimmung fuer spaetere Bypass- oder Ausnahme-Logik dokumentiert

### Scope-Klaerungen

- keine bestaetigten Cookie-, Session-, Login- und Preview-Ausnahmen
- kein dokumentierter Simulationspfad fuer anonyme gegen personalisierte Requests

### Verantwortlichkeiten

- keine verbindliche Pilot-Verantwortung dokumentiert
- keine verbindliche Rollback-Verantwortung dokumentiert

## Zusaetzlich fehlend fuer spaetere WordPress-Piloten

### Secrets oder Zugaenge

- kein WordPress-Connector-Zugang
- keine andere freigegebene Aenderungsroute fuer Theme-, Builder- oder Plugin-Ziele

### Freigaben

- keine freigegebenen WordPress-Zielbereiche
- keine Freigabe fuer Theme-, Builder- oder SEO-Plugin-bezogene Aenderungen

### Scope-Klaerungen

- unklar, welches Theme aktiv massgeblich ist
- unklar, welcher Builder aktiv massgeblich ist
- unklar, welches SEO-Plugin Title und Meta Description kontrolliert

## Optional, aber spaeter nuetzlich

- Search-Console-Zugang
- Analytics-Zugang
- weiterfuehrende CDN- oder Cache-Diagnosedaten

## Zusaetzlich fehlend fuer globalen Verkaufs- und Fulfillment-Cutover

### Secrets oder Referenzen

- reale `PAYPAL_BUSINESS_CLIENT_ID`-Referenz im Zielbetrieb
- reale `PAYPAL_BUSINESS_CLIENT_SECRET`-Referenz im Zielbetrieb
- reale `PAYPAL_BUSINESS_WEBHOOK_ID`-Referenz im Zielbetrieb
- produktionsreife Signing-Key- oder Signing-Service-Referenz

### Freigaben

- Freigabe fuer echten PayPal-Business-Zahlungsabgleich
- Freigabe fuer echten Rechnungsfluss
- Freigabe fuer geschuetzte Delivery ausserhalb des Workspace

### Verantwortlichkeiten

- verbindliche Support-Eskalation
- verbindliche Billing-/Invoice-Verantwortung
- verbindliche Operator-Freigabe fuer Customer Release
- verbindliche serverseitige Validation- und Rollback-Verantwortung im Realbetrieb

## Gate-Folgen

### Cloudflare-bezogene Change-Blueprints

- Status aktuell: `approval_required`

### WordPress-bezogene Change-Blueprints

- Status aktuell: `approval_required`

### Observe-only-Ausbau

- Status aktuell: `blueprint_ready` oder `observe_only`, je nach Daten- und Entwicklungsstand

## Doktrinische Auswirkung

Nach [AGENTS.md](/opt/electri-city-ops/AGENTS.md), [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md) und der integrierten 8.0-Quellfassung darf das Fehlen dieser Secrets und Freigaben niemals durch implizite Annahmen, Workarounds oder ausgedehnte Rechte kompensiert werden.

Folge:

- kein externer Pilot
- keine Connector-Aktivierung
- kein Wechsel aus `observe_only` in reale Wirkung
