# Real Staging Safe Mode Checklist

## Pflicht

- Plugin startet in `observe_only` oder `safe_mode`
- keine aktive Uebernahme von Head-/Meta-Ausgabe
- keine Deaktivierung anderer SEO-Plugins
- keine Scope-Ausweitung ueber `/wordpress/` und `/wordpress/beispiel-seite/`

## Beobachtung

- Homepage unter `/wordpress/`
- Beispielseite unter `/wordpress/beispiel-seite/`
- Konfliktsignale aus Theme, Builder und SEO-Plugin

## Gate

- Real Staging Safe Mode Checklist: `approval_required`
