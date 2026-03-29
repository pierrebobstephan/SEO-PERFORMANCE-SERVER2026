# Plugin Conflict Detection Model

## Zweck

Dieses Dokument beschreibt, wie Theme-, Builder- und SEO-Plugin-Konflikte spaeter erkannt werden sollen.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es priorisiert Konflikterkennung vor Wirkung.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede spaetere konfliktbeeinflusste Domain-Aktivierung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Bei Konflikt folgt Rueckfall auf `safe_mode`, `observe_only` oder `approval_required`.

## Konfliktkategorien

### Theme-Konflikte

- konkurrierende Template-Ausgabe
- mehrfach definierte Homepage-Elemente
- unklare Hook-Reihenfolge

### Builder-Konflikte

- eigene Heading- oder Wrapper-Logik
- dynamische Modulausgabe
- Editor- oder Layout-Kopplung

### SEO-Plugin-Konflikte

- doppelte Meta Description
- doppelte Title-Ausgabe
- doppelte Canonical-Tags
- widerspruechliche Robots-Ausgabe

## Erkennungslogik

Spaeter je Domain pruefen:

- aktives Theme
- aktiver Builder
- aktive SEO-Plugins
- bekannte Konfliktmuster
- bereits vorhandene Hook- oder Filter-Ausgabe

## Konfliktreaktion

- Konflikt klar und klein: `approval_required` oder enger Pilot
- Konflikt unklar: `safe_mode`
- Konflikt mit hoher Doppel-Ausgabe-Gefahr: `blocked` oder `observe_only`

## Lokale technische Verankerung

- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-conflict-detector.php`
- `docs/plugin-rank-math-coexistence-model.md`
- `tests/test_contracts.py`

## Status

- Konfliktmodell: `blueprint_ready`
- echte Konflikterkennung im Plugin: `approval_required`
