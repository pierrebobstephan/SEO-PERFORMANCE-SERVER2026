# Plugin Activation Flow

## Zweck

Dieses Dokument beschreibt den spaeteren Aktivierungsablauf des WordPress-Plugins auf einer lizenzierten Domain.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es definiert nur einen spaeteren Flow, keine Aktivierung.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede spaetere Aktivierung pro Domain ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Aktivierung kann auf Safe-Mode, `observe_only` oder Nicht-Aktivierung zurueckfallen.

## Aktivierungsfluss

1. Plugin wird lokal auf der Ziel-Domain installiert.
2. Plugin liest lokale Basiskonfiguration.
3. Plugin prueft Domain gegen `bound_domain`.
4. Plugin prueft Lizenzstatus und erlaubten Kanal.
5. Plugin prueft erlaubte Features und Scopes.
6. Plugin prueft Konfliktlage mit Theme, Builder und SEO-Plugins.
7. Plugin entscheidet zwischen:
   `safe_mode`, `observe_only`, `approval_required`, spaeter `active_scoped`

## Aktivierungs-Gates

Eine Aktivierung darf spaeter nur in `active_scoped` gehen, wenn zugleich gilt:

- Domainlizenz ist gueltig
- Domain stimmt mit der Lizenz ueberein
- erlaubter Scope ist vorhanden
- Konfliktlage ist akzeptabel
- Rollback-Profil ist bekannt
- Validierungsfenster sind bekannt

## Fallbacks

- bei ungueltiger Lizenz: `inactive`
- bei Domain-Mismatch: `observe_only`
- bei unklarer Konfliktlage: `safe_mode`
- bei fehlenden Freigaben: `approval_required`

## Rueckweg

- Aktivierung abbrechen
- Plugin im `safe_mode` oder `observe_only` belassen
- keine aktive lokale Optimierungswirkung entfalten

## Lokale technische Verankerung

- `src/electri_city_ops/product_core.py`
- `config/release-channels.json`
- `schemas/domain-binding.schema.json`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-plugin.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-license-check.php`

## Status

- Aktivierungsfluss: `blueprint_ready`
- echte Aktivierung: `approval_required`
