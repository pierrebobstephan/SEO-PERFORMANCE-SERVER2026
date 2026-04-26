# Server Migration Plan

## Ziel

Die Suite soll spaeter auf einen groesseren Hetzner-Server umziehbar bleiben.

## Migrationspfad

1. Zielserver vorbereiten.
2. Workspace-Backup und SQLite-Daten uebertragen.
3. Separate Zertifikate und Secrets sicher uebertragen.
4. Deploy-Artefakte fuer Nginx/systemd auf dem Zielserver platzieren.
5. Lokale Validierung auf dem Zielserver ausfuehren.
6. Erst danach DNS/TLS/oeffentlichen Dienst umschalten.

## Pflichtpruefungen nach Migration

- Public Portal Healthcheck
- Legal-Seiten rendern
- Protected Route Blocking
- Config-Validierung
- Test-Suite

## Grenzen

- keine Null-Ausfall-Garantie
- keine automatische horizontale Skalierung
- keine implizite Secret- oder Zertifikatssynchronisation

## Status

- Server Migration Plan: `blueprint_ready`
- reale Zielserver-Migration: `approval_required`
