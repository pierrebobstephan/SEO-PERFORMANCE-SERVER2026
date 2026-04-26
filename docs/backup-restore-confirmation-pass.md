# Backup Restore Confirmation Pass

## Ziel

Die installierte staging-only Bridge soll `backup_confirmation` und `restore_confirmation` explizit und persistent erfassen.

## Vorgehen

- beide Felder werden im WordPress-Admin unter `Operator Input Completion` gesetzt
- Speicherung erfolgt lokal und staging-only ueber die Bridge-Optionen
- sobald beide Felder gesetzt sind und keine weiteren Pflichtfelder offen sind, wird `operator_inputs_complete = true`

## Grenzen

- keine externe Zustellung
- keine Customer-Funktion
- keine Scope-Ausweitung
