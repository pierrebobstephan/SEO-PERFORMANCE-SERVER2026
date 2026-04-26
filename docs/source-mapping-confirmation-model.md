# Source Mapping Confirmation Model

## Signale

- `homepage_meta_description_single`
- `head_meta_output_single`
- `double_output_detected`
- `operator_confirmation`
- `notes`

## Confirmation-Regel

- `source_mapping_confirmed = true` nur wenn zugleich gilt:
  - `homepage_meta_description_single = true`
  - `head_meta_output_single = true`
  - `double_output_detected = false`
  - `operator_confirmation = true`
  - keine unklare Konfliktlage aktiv

## Blocker

- `double_output_detected = true`
- unklare Source-Ownership
- fehlende Operator-Bestaetigung
