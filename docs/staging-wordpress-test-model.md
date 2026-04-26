# Staging WordPress Test Model

## Ziel

Der erste echte Produkttest soll auf einer staging-/testfaehigen WordPress-Umgebung stattfinden.

## Kernregeln

- eigene Testdomain oder Test-Subdomain
- exakte licensed domain fuer Testzweck
- Plugin-Installation nur auf staging/test
- Start in `safe_mode` oder `observe_only`
- definierter Rollback-Pfad

## Nicht zulaessig

- ungeschuetzte Produktivseite als erster Realtest
- fehlendes Backup
- fehlendes Restore

## Status

- Staging WordPress Test Model: `blueprint_ready`
