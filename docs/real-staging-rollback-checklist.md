# Real Staging Rollback Checklist

## Vor Test

- Backup bestaetigt
- Restore bestaetigt
- Rollback Owner bekannt

## Rollback-Rehearsal

- Plugin deaktivierbar
- Rueckkehr in `observe_only` moeglich
- `/wordpress/` und `/wordpress/beispiel-seite/` nach Rueckbau pruefbar

## Abbruch

- Fatal Error
- Doppel-Ausgabe
- Ownership-Unklarheit
- sichtbarer Schaden

## Gate

- Real Staging Rollback Checklist: `approval_required`
