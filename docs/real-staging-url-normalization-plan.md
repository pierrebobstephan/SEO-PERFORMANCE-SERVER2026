# Real Staging URL Normalization Plan

## Ziel

Die reale staging-domain darf erst dann als sauberer Suite-Testkontext gelten, wenn WordPress nicht mehr auf `localhost` verweist.

## Erwartete Zielwerte

- expected home url: `https://wp.electri-c-ity-studios-24-7.com/wordpress/`
- expected scoped page url: `https://wp.electri-c-ity-studios-24-7.com/wordpress/beispiel-seite/`
- expected bound test host: `wp.electri-c-ity-studios-24-7.com`

## Aktueller Blocker

- staging readiness ist blockiert, solange interne Links, Canonicals, Home-/Site-URL oder interne Path-Basen noch auf `localhost` zeigen
- read-only Pruefung bestaetigt aktuell einen verbliebenen `localhost`-Rest auf der Beispielseite
- auf `/wordpress/beispiel-seite/` verweist der Standard-WordPress-Hinweis `dein Dashboard` noch auf `localhost`

## Vor echtem Pilot zwingend

- home url konsistent
- siteurl konsistent
- canonical basis konsistent
- internal path basis konsistent auf `/wordpress/`
- kein sichtbarer Dashboard-, Beispiel- oder Navigationslink darf mehr `localhost` enthalten

## Gate

- URL Normalization: `blocked`
