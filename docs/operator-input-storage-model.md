# Operator Input Storage Model

## Speicherort

- packaged defaults: `packages/wp-plugin/hetzner-seo-ops/config/bridge-config.json`
- lokale Runtime-Overrides: WordPress Option `hso_bridge_operator_inputs`

## Persistierte Felder

- `backup_confirmation`
- `restore_confirmation`
- `rollback_owner`
- `validation_owner`

## Laufzeit-Vorbelegung

- `wordpress_version` aus WordPress Runtime
- `active_theme` aus Theme-Snapshot
- `active_builder` aus Conflict-Snapshot oder `none`
- `active_seo_plugin` aus Conflict-Snapshot oder `none`
- `plugin_inventory` aus aktivem Plugin-Inventar

## Gate-Regel

- `operator_inputs_complete = true` nur wenn alle Pflichtfelder komplett sind
