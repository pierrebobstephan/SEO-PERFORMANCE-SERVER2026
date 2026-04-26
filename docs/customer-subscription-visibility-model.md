# Customer Subscription Visibility Model

## Zweck

Dieses Dokument beschreibt, welche kaeuferlesbaren Daten eine installierte Bridge spaeter lokal sichtbar machen darf.

## Sichtbare Felder

- `license_id`
- `subscription_status`
- `renewal_state`
- `renewal_window_state`
- `failed_payment_recovery_state`
- `bound_domain`
- `current_domain`
- `domain_match`
- `domain_scope_summary`
- `documentation_access`
- `licensed_download_access`
- `license_integrity_state`
- `support_state`
- `activation_state`
- `subscription_lifecycle_note`

## Regeln

- Die Sicht ist plugin-intern und admin-only.
- Sie darf keine Customer-Routen, kein Login und keine offene Delivery vortaeuschen.
- Unbestaetigte Felder bleiben `operator input required`, `source not yet confirmed` oder `approval_required`.

## Status

- Sichtmodell: `blueprint_ready`
- echte abonnentenweite Customer-Plattform: `approval_required`
