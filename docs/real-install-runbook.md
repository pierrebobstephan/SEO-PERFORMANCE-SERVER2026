# Real Install Runbook

## Ziel

Das staging-only Pilotpaket soll auf der realen WordPress-Testumgebung kontrolliert installiert werden.

## Install Steps

1. Backup bestaetigen.
2. Restore-Bestaetigung dokumentieren.
3. URL-Normalisierung erfolgreich gegenpruefen.
4. das Paket `dist/staging-only/site-optimizer-bridge-0.1.0-real-staging1-wp-electri-c-ity-studios-24-7-com.zip` lokal bereithalten.
5. im WordPress-Admin nur der staging-domain das Plugin-Paket hochladen.
6. nach dem Upload die Plugin-Dateien und die Version `0.1.0-real-staging1` gegenpruefen.

## Activation Steps

1. Plugin aktivieren.
2. bestaetigen, dass der Startmodus `safe_mode` oder `observe_only` ist.
3. keine Scope-Ausweitung vornehmen.

## Validation Steps

1. `/wordpress/` laden.
2. `/wordpress/beispiel-seite/` laden.
3. Head-, Meta-, Structure- und Visibility-Diagnostics pruefen.
4. Stop-Bedingungen gegenpruefen.

## Rollback Steps

1. Plugin deaktivieren.
2. wenn noetig Plugin entfernen.
3. Vorher-Zustand der beiden URLs und der Ownership-Signale bestaetigen.

## Gate

- Real Install Runbook: `approval_required`
