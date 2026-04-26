# License and Domain Binding Model

## Zweck

Dieses Dokument beschreibt, wie spaeter eine Lizenz an eine WordPress-Domain gebunden wird, ohne die Doktrin zu verletzen.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es beschreibt nur ein spaeteres Lizenz- und Scope-Modell.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede spaetere Lizenzaktivierung pro Domain ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Eine Domain kann auf deaktivierte Lizenz, `observe_only` oder Rollback-Policy zurueckfallen.

## Lizenzobjekt

Jede spaetere Lizenz sollte mindestens enthalten:

- `license_id`
- `customer_id`
- `product_id`
- `domain_binding.bound_domain`
- `domain_binding.allowed_subdomains`
- `domain_binding.release_channel`
- `policy_channel`
- `allowed_scopes`
- `allowed_features`
- `status`
- `issued_at`
- `expires_at` oder `non_expiring`
- `rollback_profile_id`
- `integrity.signature`
- `integrity.signature_state`
- `integrity.signing_key_reference`

## Domain-Binding

Eine Lizenz wird an genau eine produktive Hauptdomain gebunden.

Optionale Erweiterung:

- klar benannte Zusatz-Subdomain(s), falls ausdruecklich freigegeben

Zusatzregeln:

- jede erlaubte Subdomain muss eine explizite Unterdomain der Hauptdomain sein
- die Hauptdomain darf nicht in `allowed_subdomains` wiederholt werden
- Duplikate in `allowed_subdomains` sind unzulaessig

Nicht erlaubt ohne Sonderfreigabe:

- wildcard-domain-Bindings
- siteweite Mehrdomain-Freischaltung unter einer unbestimmten Lizenz
- Lizenz-Sharing zwischen getrennten Kundenprojekten

## Aktivierungslogik

- das Plugin prueft spaeter lokal, ob die aktuelle Domain mit der gebundenen Lizenz uebereinstimmt
- bei Nicht-Uebereinstimmung darf keine aktive Optimierungswirkung entstehen
- bei Unsicherheit faellt die Domain auf `observe_only` oder `approval_required` zurueck

## Scope-Bindung

Neben der Domain muss auch der fachliche Scope gebunden werden:

- Homepage-only
- klar benannte Templates
- klar benannte Plugin-Hooks
- spaeter freigegebene Seitentypen

Keine Lizenz darf automatisch globale Theme-, Builder- oder SEO-Eingriffe freischalten.

## Statusmodell

- `inactive`
- `observe_only`
- `approval_required`
- `pilot_ready`
- `active_scoped`
- `rollback_required`
- `revoked`

## Rueckweg

- Lizenz auf `inactive` oder `revoked`
- Domain faellt auf lokale Nicht-Anwendung zurueck
- Rollback-Profil steuert, welche lokale Ruecknahme fuer die Domain gilt

## Lokale technische Verankerung

- `schemas/domain-binding.schema.json`
- `schemas/license-object.schema.json`
- `src/electri_city_ops/product_core.py`
- `docs/license-object-spec.md`

## Status

- Lizenzmodell: `implemented_locally`
- produktive Lizenzbindung: `approval_required`
