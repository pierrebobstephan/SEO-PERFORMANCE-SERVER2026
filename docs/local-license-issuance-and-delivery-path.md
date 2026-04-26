# Local License Issuance And Delivery Path

## Zweck

Dieses Dokument beschreibt den lokalen produktionsnahen Pfad zwischen Lizenzobjekt, Entitlement, Install-Paket und installierter Bridge.

## Lokaler Pfad

1. Plugin-Paket bauen
2. Lizenzobjekt lokal vorbereiten
3. Manifest lokal vorbereiten
4. Entitlement lokal vorbereiten
5. Rollback- und Validation-Artefakte referenzieren
6. geschuetzten Install-Pack lokal erzeugen
7. Bridge zeigt diese Daten nur im Admin an

## Grenzen

- keine offene Lizenz-API
- keine offene Download-Ausgabe
- keine Customer-Authentifizierung
- keine geschuetzten Routen im Public Portal

## Status

- lokaler Pfad: `blueprint_ready`
- reale Ausgabe: `approval_required`
