# Operator Input Closure Pass

## Ziel

Offene Pflichtinputs sollen sauber geschlossen werden, ohne dass stale Packaged-Zustaende die Runtime-Ableitung uebersteuern.

## Pflichtfelder in diesem Schritt

- `backup_confirmation`
- `restore_confirmation`
- `rollback_owner`
- `validation_owner`

## Regel

- `rollback_owner` und `validation_owner` duerfen server-managed durch die Bridge kommen
- `backup_confirmation` und `restore_confirmation` bleiben explizite staging-only Operator-Eintraege
- `operator_inputs_complete` darf nur aus dem echten Runtime-Zustand abgeleitet werden
