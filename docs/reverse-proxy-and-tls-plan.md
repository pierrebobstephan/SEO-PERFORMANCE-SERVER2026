# Reverse Proxy and TLS Plan

## Zweck

Dieses Dokument beschreibt Reverse Proxy, TLS und den serverseitigen Pfad zur oeffentlichen Subdomain.

## Geplanter Upstream

- Public portal app: `127.0.0.1:8781`
- Operator-Konsole bleibt getrennt auf `127.0.0.1:8765`

## Nginx

- HTTP -> HTTPS Redirect
- TLS-Termination im vHost
- Proxy nur auf Public-Portal-Upstream
- protected routes im Proxy geblockt

## TLS

- bevorzugt Let s Encrypt oder bestaetigtes vorhandenes Zertifikatsmodell
- Zertifikat und Key bleiben ausserhalb des Repos
- Healthcheck bleibt lokal und ueber HTTPS pruefbar

## Artefakte

- `deploy/nginx/site-optimizer.electri-c-ity-studios-24-7.com.conf.example`
- `deploy/nginx/snippets/site-optimizer-protected-routes.conf.example`
- `deploy/systemd/electri-city-public-portal.service.example`
- `deploy/healthchecks/site-optimizer-portal-healthcheck.sh.example`

## Status

- Reverse-Proxy- und TLS-Plan: `blueprint_ready`
- echte Aktivierung: `approval_required`
