# Final Staging Pilot Package Plan

## Ziel

Ein lokal gebautes, installierbares, aber strikt staging-only Pilotpaket wird fuer `wp.electri-c-ity-studios-24-7.com` vorbereitet.

## Paketprofil

- plugin slug: `hetzner-seo-ops`
- plugin version: `0.1.0-real-staging1`
- release channel: `pilot`
- target host: `wp.electri-c-ity-studios-24-7.com`
- path base: `/wordpress/`
- default mode: `safe_mode`
- fallback mode: `observe_only`

## Scope V1

- homepage meta diagnostics
- head diagnostics
- structure diagnostics
- visibility diagnostics

## Gate

- Final Staging Pilot Package Plan: `approval_required`
- Ready-for-real-install state: `blocked` bis URL-Normalisierung sauber ist
