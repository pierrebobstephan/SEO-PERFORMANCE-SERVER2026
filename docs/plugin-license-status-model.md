# Plugin License Status Model

## Zweck

Dieses Dokument beschreibt das lokale Lizenzstatusmodell innerhalb des WordPress-Plugins.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Das Modell schaltet nie Sicherheit aus.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Spaetere reale Lizenzpruefungen ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Nicht-Match oder Unsicherheit fuehren auf `observe_only`, `safe_mode` oder `approval_required`.

## Lokale Kernfelder

- `license_id`
- `customer_id`
- `product_id`
- `status`
- `bound_domain`
- `allowed_subdomains`
- `allowed_scopes`
- `allowed_features`
- `release_channel`
- `policy_channel`
- `rollback_profile_id`
- `issued_at`
- `expires_at` oder `non_expiring`
- `integrity.signature_state`
- `integrity.signing_key_reference`
- `operator_inputs_complete`
- `domain_match`

## Interpretation

- fehlende `bound_domain`: `observe_only`
- `inactive` oder `revoked`: `observe_only`
- unvollstaendige Freigaben oder unklare Source-Mapping-Lage: `approval_required`
- mehrdeutige Konflikte: `safe_mode`
- `active_scoped` nur bei bestaetigter Lizenz-, Domain-, Scope-, Policy-, Validation-, Rollback- und Integritaetslage

## Status

- Lizenzstatusmodell: `implemented_locally`
- echte Lizenzantworten: `approval_required`
