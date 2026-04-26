# Operator Protected Fulfillment Runbook

## Zweck

Dieses Runbook beschreibt die lokale, geschuetzte Vorbereitung eines Customer-Install-Packs fuer die Bridge.

## Schritte

1. Paket-Metadaten pruefen
2. Lizenzobjekt pruefen
3. Manifest pruefen
4. Entitlement pruefen
5. Rollback- und Validation-Artefakte pruefen
6. geschuetzten Install-Pack lokal bauen
7. kaeuferlesbare Plugin-Sicht gegen Install-Pack abgleichen

## Abort

- Domain-Bindung unklar
- Scope unklar
- Rollback/Validation fehlen
- Delivery waere nicht mehr protected

## Status

- Runbook: `blueprint_ready`
- echte Customer-Ausgabe: `approval_required`
