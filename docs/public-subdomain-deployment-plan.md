# Public Subdomain Deployment Plan

## Zweck

Dieses Dokument beschreibt die kontrollierte Deployment-Vorbereitung fuer die oeffentliche Produkt-Subdomain.

## Gewaehlte Subdomain

- `site-optimizer.electri-c-ity-studios-24-7.com`

## Warum diese Wahl

- semantisch klar fuer WordPress SEO und Performance
- kompakter als die lange Suite-Variante
- breiter als nur `wp-optimizer`, weil auch Control-Plane-, Lizenz- und Sicherheitslogik kommuniziert werden

## Deployment-Ziel

- oeffentlich: Produktportal, Landing, Doku-Einstieg, Support, gated Download-Layer
- nicht oeffentlich: Operator-Konsole, Control Plane, Lizenz-API, Customer-Execution-Pfade

## Lokale Artefakte

- `src/electri_city_ops/public_portal.py`
- `tools/run_public_portal.py`
- `config/public-portal.json`
- `deploy/nginx/site-optimizer.electri-c-ity-studios-24-7.com.conf.example`
- `deploy/systemd/electri-city-public-portal.service.example`

## Geplanter Pfad

1. Portal-App lokal auf `127.0.0.1:8781` starten
2. Nginx davor schalten
3. HTTP auf HTTPS umleiten
4. TLS aktivieren
5. nur Public-Routen freigeben
6. protected routes auf `404` oder spaeter starke Auth stellen

## Status

- serverbereit lokal vorbereitet: `blueprint_ready`
- echte oeffentliche Freischaltung: `approval_required`
