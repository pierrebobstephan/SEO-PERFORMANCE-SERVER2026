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
- `bound_domain`
- `allowed_subdomain_policy`
- `plugin_channel`
- `policy_channel`
- `allowed_scopes`
- `allowed_features`
- `status`
- `issued_at`
- `expires_at` oder `non_expiring`
- `rollback_profile`

## Domain-Binding

Eine Lizenz wird an genau eine produktive Hauptdomain gebunden.

Optionale Erweiterung:

- klar benannte Zusatz-Subdomain(s), falls ausdruecklich freigegeben

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

## Status

- Lizenzmodell: `blueprint_ready`
- produktive Lizenzbindung: `approval_required`
