# First Real Staging Test Checklist

## Pflicht vor Teststart

- staging/test domain bestaetigt
- exakte licensed test domain dokumentiert
- Backup bestaetigt
- Restore bestaetigt
- Rollback Owner benannt
- Validation Owner benannt
- Theme/Builder/SEO-Plugin-Bild dokumentiert
- Plugin-Inventar dokumentiert

## Pflicht waehrend Test

- Plugin in `observe_only` oder `safe_mode`
- kein Scope-Austritt
- keine Ownership-Uebernahme bei Unklarheit
- keine Deaktivierung anderer SEO-Plugins

## Pflicht nach Test

- Ergebnisse sichern
- Rollback-Rehearsal pruefen
- Outcome als passed, inconclusive oder failed einstufen

## Gate

- First Real Staging Test Checklist: `approval_required`
