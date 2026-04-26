# Source Mapping Gate Reconciliation

## Ziel

`source_mapping_confirmed` soll nur aus echtem Runtime-Zustand folgen und nicht aus stale Packaged-Flags.

## Runtime-Signale

- `homepage_meta_description_single`
- `head_meta_output_single`
- `operator_confirmation`
- `double_output_verification`
- `source_mapping_unclear`
- `baseline captured`

## Ableitungsregel

- `operator source mapping confirmation is still required` darf nur offen bleiben, wenn `operator_confirmation = false`
- ein altes Packaged-Flag allein darf keinen offenen Runtime-Blocker erzeugen
- `source_mapping_confirmed = true` nur wenn:
  - Homepage Ownership bestaetigt ist
  - Head/Meta Single-Source bestaetigt ist
  - Operator bestaetigt hat
  - kein real bestaetigter Duplicate-Output offen ist
  - keine echte Ownership-Kollision offen ist
