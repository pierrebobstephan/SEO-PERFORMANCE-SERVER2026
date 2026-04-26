# First Test Observe Only Metrics

## Beobachtbare Daten

- Plugin laedt ohne Fatal Error
- Diagnostics werden erzeugt
- Konflikte werden erfasst
- Domain-/Scope-Pruefung bleibt korrekt
- Rollback-Pfad bleibt intakt

## Erhebungsgrenzen

- nur staging/test Daten
- keine riskante cross-domain Generalisierung
- keine Customer- oder Produktivdaten ausserhalb des freigegebenen Testscopes

## Gate

- First Test Observe Only Metrics: `approval_required`
