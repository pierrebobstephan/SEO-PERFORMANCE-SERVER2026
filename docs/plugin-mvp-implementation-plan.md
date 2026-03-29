# Plugin MVP Implementation Plan

## Zweck

Dieses Dokument beschreibt das lokale WordPress-Plugin-MVP fuer den doctrine-konformen Ausfuehrungspfad. Der aktuelle Stand ist rein lokal, ohne Auslieferung, ohne Aktivierung und ohne externe Wirkung.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Das Plugin bleibt standardmaessig `observe_only`, `safe_mode` oder `approval_required`.
2. Bleibt es innerhalb des Workspace?
   Ja. Die lokale Struktur liegt unter `packages/wp-plugin/hetzner-seo-ops`.
3. Hat es irgendeine externe Wirkung?
   Nein. Es wird nicht installiert oder verbunden.
4. Braucht es Approval?
   Das lokale MVP nicht. Jede spaetere Auslieferung oder Installation ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Safe-Mode, Nicht-Auslieferung und Rollback-Registry sind Teil des MVP.

## Lokale Artefakte

- `packages/wp-plugin/hetzner-seo-ops/hetzner-seo-ops.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-plugin.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-license-check.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-safe-mode.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-conflict-detector.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-rollback-registry.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-validation-status.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/modules/class-hso-meta-description-module.php`
- `packages/wp-plugin/hetzner-seo-ops/admin/class-hso-admin-screen.php`

## MVP-Ziele

- doctrine-konformer Bootstrap
- lokaler License- und Domain-Status-Snapshot
- `observe_only` und `safe_mode` als Default-Fallbacks
- Konflikterkennung fuer Theme, Builder und SEO-Plugins
- lokaler Rollback- und Validation-Skeleton
- erster kontrollierter Homepage-Meta-Description-Pilot als Modul, standardmaessig deaktiviert

## Nicht-Ziele in dieser Phase

- keine Live-Installation
- kein WordPress-Connector
- keine Rank-Math-Ablosung
- keine aktive Meta-Ausgabe ohne bestaetigte Quellenzuordnung
- keine siteweiten Massnahmen

## Gate-Status

- Plugin-MVP lokal: `blueprint_ready`
- Plugin Pilot 1: `approval_required`
- reale Auslieferung: `approval_required`
