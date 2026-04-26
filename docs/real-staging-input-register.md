# Real Staging Input Register

## Bekannte Inputs

- public wordpress base url: `https://wp.electri-c-ity-studios-24-7.com/wordpress/`
- scoped test page: `https://wp.electri-c-ity-studios-24-7.com/wordpress/beispiel-seite/`
- bound test host: `wp.electri-c-ity-studios-24-7.com`
- path base: `/wordpress/`
- package version for staging-only build: `0.1.0-real-staging1`
- default plugin mode: `safe_mode`
- fallback plugin mode: `observe_only`
- current residual blocker: the example page dashboard hint still points to `localhost`

## Weiter offen

- WordPress version
- active theme
- active builder
- active SEO plugin
- plugin inventory
- backup confirmation
- restore confirmation
- rollback owner
- validation owner

## Gate

- Real Staging Input Register: `approval_required`
- Ready-for-real-install gate: `blocked`
