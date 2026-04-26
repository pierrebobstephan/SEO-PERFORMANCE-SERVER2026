# License Object Spec

## Zweck

Dieses Dokument spezifiziert das technische Lizenzobjekt fuer das kontrolliert produktionsreife WordPress-Produkt.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es beschreibt nur die Struktur eines spaeteren Lizenzobjekts.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede spaetere Domainlizenz und Aktivierung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Lizenzstatus und Rollback-Profil sind Teil des Objekts.

## Kernfelder

Ein kontrolliert freigabefaehiges Lizenzobjekt muss mindestens enthalten:

- `license_id`
- `customer_id`
- `product_id`
- `domain_binding.bound_domain`
- `domain_binding.allowed_subdomains`
- `domain_binding.allowed_scopes`
- `domain_binding.release_channel`
- `domain_binding.policy_channel`
- `domain_binding.rollback_profile_id`
- `allowed_features`
- `status`
- `issued_at`
- `expires_at` oder `non_expiring`
- `integrity.signature`
- `integrity.signature_state`
- `integrity.signing_key_reference`

## Statuswerte

- `inactive`
- `observe_only`
- `approval_required`
- `pilot_ready`
- `active_scoped`
- `rollback_required`
- `revoked`

## Bindungsregeln

- eine Lizenz bindet genau eine Hauptdomain
- zusaetzliche Subdomains nur, wenn explizit in `allowed_subdomains` dokumentiert
- jede erlaubte Subdomain muss ein expliziter Nachfahre der `bound_domain` sein
- `allowed_subdomains` darf die `bound_domain` nicht wiederholen
- `allowed_subdomains` darf keine Duplikate enthalten
- keine unbestimmten Wildcard-Freigaben
- keine automatische Uebertragung auf andere Kundenprojekte

## Scope-Regeln

`allowed_scopes` sollte spaeter nur klar begrenzte Bereiche beschreiben, zum Beispiel:

- `homepage_only`
- `template:front-page.php`
- `hook:wp_head`
- `feature:meta_description`

Nicht zulaessig als Default:

- globale Theme- oder Builder-Freigaben
- siteweite Mehrdeutigkeit
- unbestimmte Wildcard-Scope-Definitionen

## Integritaet und Vertrauenskette

Die Lizenz muss pruefbar sein auf:

- Domain-Uebereinstimmung
- Kanal-Uebereinstimmung
- Scope-Uebereinstimmung
- Integritaet des Lizenzobjekts
- Signaturstatus und Signing-Key-Referenz

## Rueckweg

- Statuswechsel auf `inactive`, `revoked` oder `rollback_required`
- Rueckfall des Plugins auf lokale Nicht-Anwendung oder Safe-Mode

## Lokale technische Verankerung

Diese Spezifikation ist jetzt lokal an folgende Artefakte gebunden:

- `schemas/license-object.schema.json`
- `schemas/domain-binding.schema.json`
- `src/electri_city_ops/product_core.py`
- `tests/test_product_core.py`

## Status

- Lizenzobjekt-Spezifikation: `implemented_locally`
- produktive Nutzung: `approval_required`
