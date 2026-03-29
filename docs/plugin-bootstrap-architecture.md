# Plugin Bootstrap Architecture

## Zweck

Dieses Dokument beschreibt den spaeteren Bootstrap des WordPress-Plugins auf einer lizenzierten Domain.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es beschreibt nur die spaetere Initialisierungslogik.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede spaetere Plugin-Ausfuehrung pro Domain ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Bootstrap kann in `safe_mode` oder `observe_only` enden.

## Bootstrap-Stufen

### 1. Minimalstart

- Plugin laedt nur Basiskonfiguration
- keine aktive Optimierung

### 2. Domain- und Lizenzpruefung

- Domain mit Lizenzobjekt abgleichen
- Status und Kanal pruefen

### 3. Policy- und Scope-Ladung

- erlaubte Features laden
- erlaubte Scopes laden
- Konfliktblockliste laden

### 4. Konfliktpruefung

- Theme
- Builder
- SEO-Plugin
- bekannte Hook-Konflikte

### 5. Modusentscheidung

- `safe_mode`
- `observe_only`
- `approval_required`
- spaeter `active_scoped`

## Bootstrap-Prinzip

Standard ist nicht aktive Wirkung, sondern defensiver Start.

Nur wenn alle Gates sauber sind, darf spaeter aus Bootstrap heraus in einen anwendenden Zustand gewechselt werden.

## Rueckweg

- Rueckfall in `safe_mode`
- Rueckfall in `observe_only`
- lokale Deaktivierung anwendungsnaher Features

## Lokale technische Verankerung

- `packages/wp-plugin/hetzner-seo-ops/hetzner-seo-ops.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-plugin.php`
- `packages/wp-plugin/hetzner-seo-ops/admin/class-hso-admin-screen.php`
- `docs/plugin-mvp-implementation-plan.md`

## Status

- Bootstrap-Architektur: `blueprint_ready`
- echte Plugin-Bootstrap-Wirkung: `approval_required`
