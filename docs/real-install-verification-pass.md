# Real Install Verification Pass

## Ziel

Nach der Installation pruefen, dass das Plugin wirklich korrekt geladen ist.

## Pruefpunkte

- Plugin erscheint im WordPress-Admin als installiert
- Version `0.1.0-real-staging1` ist sichtbar
- Aktivierung fuehrt nicht zu Fatal Errors
- Startmodus ist `safe_mode` oder `observe_only`
- `/wordpress/` und `/wordpress/beispiel-seite/` bleiben erreichbar

## Gate

- Real Install Verification Pass: `approval_required`
