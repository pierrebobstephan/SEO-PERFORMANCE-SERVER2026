# License Check API Contract

## Zweck

Dieses Dokument beschreibt das spaetere, domaingebundene Lizenzpruefobjekt fuer das Plugin. Es ist aktuell nur lokal als Vertragsmodell angelegt.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Lizenzdaten schalten keine Sicherheitsgrenzen aus.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Vertragsdokument nicht. Jede spaetere reale API-Nutzung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ungueltige oder fehlende Antworten fuehren auf sichere Fallback-Modi.

## Vertragsfelder

- `response_status`
- `signature_status`
- `license`
- `issued_at`

Die eingebettete `license` referenziert lokal:

- `schemas/license-object.schema.json`

## Interpretationsregeln

- nur `response_status = ok` ist verwertbar
- `signature_status = untrusted` ist nicht aktivierungsfaehig
- Domain- und Scope-Bindung werden aus dem Lizenzobjekt gelesen
- fehlende oder ungueltige Antwort erzwingt `observe_only` oder `safe_mode`

## Status

- Lizenzvertrag: `blueprint_ready`
- echte API-Nutzung: `approval_required`
