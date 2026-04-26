# Operator Input Completion Runbook

## Ziel

- die vier noch offenen staging-only Operator-Inputs lokal setzen
- keine Oeffnung von Customer-, Login- oder Public-Delivery-Pfaden

## Pflichtfelder

- `backup_confirmation`
- `restore_confirmation`
- `rollback_owner`
- `validation_owner`

## Ablauf

1. WordPress Admin `Site Optimizer` oeffnen
2. Bereich `Operator Input Completion` pruefen
3. Laufzeitfelder nur lesen:
   - `wordpress_version`
   - `active_theme`
   - `active_builder`
   - `active_seo_plugin`
   - `plugin_inventory`
4. Die vier Operator-Felder ausfuellen
5. `Save Operator Inputs` ausfuehren
6. Nach Redirect pruefen:
   - offene Felder reduziert
   - `operator_inputs_complete` nur dann `true`, wenn keine Pflichtfelder mehr fehlen

## Grenzen

- nur staging-only
- keine Scope-Ausweitung
- keine Optimierungsfreigabe ohne gruene Eligibility
