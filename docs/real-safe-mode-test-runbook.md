# Real Safe Mode Test Runbook

## Startbedingung

- Plugin ist installiert
- URL-Normalisierung ist sauber
- Backup und Restore sind bestaetigt

## Testablauf

1. Plugin nur in `safe_mode` oder `observe_only` starten.
2. Homepage unter `/wordpress/` pruefen.
3. Beispielseite unter `/wordpress/beispiel-seite/` pruefen.
4. sichtbare Head-, Meta-, Structure- und Visibility-Diagnostics erfassen.
5. keine aktive Ownership-Uebernahme erlauben.

## Sofortige Stop-Bedingungen

- fatal error
- sichtbare Seitenschaedigung
- doppelte Meta- oder Head-Ausgabe
- unklare Ownership
- domain mismatch
- rollback path broken

## Erfolgsbild

- keine Fatal Errors
- keine sichtbare Seitenschaedigung
- reproduzierbare Diagnostics
- Rollback bleibt intakt

## Gate

- Real Safe Mode Test Runbook: `approval_required`
