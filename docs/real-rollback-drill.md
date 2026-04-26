# Real Rollback Drill

## Ziel

Den Rueckbau auf der staging-domain praktisch und reproduzierbar pruefen.

## Drill

1. Plugin deaktivieren.
2. wenn noetig Plugin entfernen.
3. `/wordpress/` und `/wordpress/beispiel-seite/` gegen Vorher-Zustand pruefen.
4. bestaetigen, dass keine doppelte Meta-/Head-Ausgabe bleibt.
5. Rollback-Owner dokumentiert das Ergebnis.

## Gate

- Real Rollback Drill: `approval_required`
