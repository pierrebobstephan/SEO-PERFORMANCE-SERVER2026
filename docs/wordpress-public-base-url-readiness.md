# WordPress Public Base URL Readiness

## Erwartete Basis

- public wordpress base url: `https://wp.electri-c-ity-studios-24-7.com/wordpress/`
- path base: `/wordpress/`
- scoped test page: `https://wp.electri-c-ity-studios-24-7.com/wordpress/beispiel-seite/`

## Readiness-Regel

- die Umgebung ist nicht staging-ready, solange WordPress intern noch `localhost` als Basis verwendet
- vor echtem Test muessen Home-/Site-URL, Canonicals und interne Links auf die reale Domain zeigen

## Gate

- Public Base URL Readiness: `blocked`
