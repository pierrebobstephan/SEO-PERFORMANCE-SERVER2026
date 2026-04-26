# Local Signed Delivery Prep Model

## Zweck

Dieses Dokument beschreibt die lokale, produktionsnahe Vorbereitung fuer spaetere signierte Delivery von Plugin, Manifest, Lizenzobjekt und Entitlement.

## Grundregeln

- keine Klartext-Secrets im Workspace
- keine echten Signaturen ohne freigegebenen Schluesselpfad
- nur Digest-, Key-Reference- und Replay-Prep lokal
- Delivery bleibt `protected_local_only`

## Lokale Artefakte

- `manifests/previews/final-real-staging-signed-delivery-prep.json`
- `manifests/previews/final-real-staging-license-issuance-prep.json`

## Status

- Modell: `blueprint_ready`
- reale Signatur und Delivery: `approval_required`
