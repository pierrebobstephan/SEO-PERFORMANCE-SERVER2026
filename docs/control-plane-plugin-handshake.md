# Control Plane Plugin Handshake

## Zweck

Dieses Dokument beschreibt die lokale Vertragsvorbereitung zwischen Hetzner Control Plane und WordPress-Plugin, ohne echte API oder Aktivierung.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Der Handshake erweitert nur die lokale Sicherheits- und Vertragslogik.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Vertragsmodell nicht. Jede spaetere echte Verbindung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Fehlende oder ungueltige Vertragsdaten fuehren auf `observe_only`, `safe_mode` oder `approval_required`.

## Handshake-Schritte

1. Plugin liest lokale Runtime-Basis
2. Plugin bewertet aktuelle Domain
3. Plugin interpretiert spaeter eine License-Check-Response
4. Plugin interpretiert spaeter eine domaingebundene Policy-Response
5. Plugin interpretiert spaeter ein domaingebundenes Rollback-Profil
6. Plugin bestimmt daraus Modus und erlaubten Scope
7. bei Unsicherheit gilt `observe_only`, `safe_mode` oder `approval_required`

## Lokale Artefakte

- `src/electri_city_ops/contracts.py`
- `schemas/license-check-response.schema.json`
- `schemas/plugin-policy-response.schema.json`
- `schemas/rollback-profile.schema.json`
- `schemas/customer-domain-onboarding.schema.json`

## Status

- Handshake-Modell: `blueprint_ready`
- echte Verbindung: `approval_required`
