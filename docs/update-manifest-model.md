# Update Manifest Model

## Zweck

Dieses Dokument beschreibt das spaetere Manifest fuer Plugin-Download, Updates, Policies und Rollback-Hinweise.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es beschreibt nur ein spaeteres Metadatenmodell.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede spaetere Manifest-Auslieferung pro Domain ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Rollback-Versionen und Rollback-Profile sind Teil des Modells.

## Manifest-Felder

Ein spaeteres Update-Manifest sollte mindestens enthalten:

- `product_id`
- `plugin_version`
- `release_channel`
- `license_id`
- `bound_domain`
- `package_url` oder anderer kontrollierter Bezugswert
- `package_checksum`
- `policy_version`
- `rollback_version`
- `allowed_scopes`
- `required_features`
- `conflict_blocklist_version`
- `min_plugin_version`
- `issued_at`

## Zweck des Manifests

- Plugin-Download domaingebunden beschreiben
- Update-Berechtigung domaingebunden beschreiben
- Policy-Version und Rollback-Option verknuepfen
- Kanal und Scope klar binden

## Nicht erlaubt

- globales Manifest fuer unbestimmte Domains
- kanalunabhaengige Massenfreigabe
- Updates ohne Rollback-Referenz

## Rueckweg

- Manifest kann spaeter auf vorherige Version zeigen
- Domain kann auf `rollback`-Kanal oder `safe_mode` fallen

## Lokale technische Verankerung

- `schemas/update-manifest.schema.json`
- `src/electri_city_ops/product_core.py`
- `docs/plugin-update-check-flow.md`

## Status

- Manifest-Modell: `blueprint_ready`
- echte Manifest-Auslieferung: `approval_required`
