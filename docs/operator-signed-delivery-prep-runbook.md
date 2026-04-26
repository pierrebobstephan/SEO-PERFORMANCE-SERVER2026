# Operator Signed Delivery Prep Runbook

## Zweck

Dieses Runbook beschreibt den lokalen Operator-Pfad vor spaeterer signierter Plugin- und Lizenz-Delivery.

## Schritte

1. Plugin-ZIP und Package-Metadaten bestaetigen
2. Lizenzobjekt, Manifest und Entitlement bestaetigen
3. geschuetzten Install-Pack bestaetigen
4. Digest-Satz bauen
5. Signing-Key-Referenz dokumentieren
6. Replay-Protection-Strategie dokumentieren
7. Delivery Grant im Status `approval_required` halten

## Abort

- Schluesselpfad unklar
- Digest-Satz unvollstaendig
- Delivery waere oeffentlich oder scope-unklar
- Rollback oder Validation fehlen

## Status

- Runbook: `blueprint_ready`
- reale signierte Delivery: `approval_required`
