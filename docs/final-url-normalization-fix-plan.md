# Final URL Normalization Fix Plan

## Ziel

Der letzte reale Staging-Blocker ist ein verbliebener `localhost`-Verweis in der WordPress-Testumgebung. Vor einem echten kontrollierten Installations- und Testlauf muessen Home-, Site-, Canonical- und Beispielseiten-Links vollstaendig auf die reale Domain zeigen.

## Erwartete Zielwerte

- expected home url: `https://wp.electri-c-ity-studios-24-7.com/wordpress/`
- expected example page url: `https://wp.electri-c-ity-studios-24-7.com/wordpress/beispiel-seite/`
- expected admin base for dashboard-related hints: `https://wp.electri-c-ity-studios-24-7.com/wordpress/wp-admin/`
- expected bound test host: `wp.electri-c-ity-studios-24-7.com`

## Aktuelle Ist-Lage

- die WordPress-Basis ist oeffentlich erreichbar
- die Beispiel-Seite ist oeffentlich erreichbar
- auf der Beispiel-Seite zeigt der Standard-WordPress-Hinweis `dein Dashboard` noch auf `localhost`

## Minimaler reversibler Fix-Pfad

1. Datenbank-Backup bestaetigen.
2. `home` und `siteurl` read-only pruefen.
3. einen `search-replace` erst als Dry-Run ausfuehren.
4. nur wenn die betroffenen Zeilen erwartbar und klein sind, den Write-Schritt staging-only ausfuehren.
5. Home und Beispiel-Seite sofort gegenpruefen.

## Copyable WP-CLI Vorbereitung

```bash
wp --url='https://wp.electri-c-ity-studios-24-7.com/wordpress/' option get home
wp --url='https://wp.electri-c-ity-studios-24-7.com/wordpress/' option get siteurl
wp --url='https://wp.electri-c-ity-studios-24-7.com/wordpress/' search-replace \
  'http://localhost/wordpress/' \
  'https://wp.electri-c-ity-studios-24-7.com/wordpress/' \
  --skip-columns=guid \
  --precise \
  --all-tables-with-prefix \
  --dry-run \
  --report-changed-only
```

## Write-Schritt nur nach Backup und Dry-Run-Freigabe

```bash
wp --url='https://wp.electri-c-ity-studios-24-7.com/wordpress/' search-replace \
  'http://localhost/wordpress/' \
  'https://wp.electri-c-ity-studios-24-7.com/wordpress/' \
  --skip-columns=guid \
  --precise \
  --all-tables-with-prefix \
  --report-changed-only
```

## Verifikation danach

- Home unter `/wordpress/` zeigt keine `localhost`-Links mehr
- Beispielseite unter `/wordpress/beispiel-seite/` zeigt keine `localhost`-Links mehr
- der Dashboard-Hinweis zeigt nicht mehr auf `localhost`
- Canonical- und interne URL-Basis zeigen auf `wp.electri-c-ity-studios-24-7.com`

## Gate

- Final URL Normalization Fix Plan: `blocked` bis keine `localhost`-Reste mehr sichtbar sind
