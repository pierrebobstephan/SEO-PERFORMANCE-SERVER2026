# WordPress Bridge PHP Validation Gate

## Zweck

Dieses Gate stellt sicher, dass der gepackte WordPress-Bridge-Code vor einem produktiven Claim mindestens eine PHP-Syntaxpruefung durchlaufen hat.

## Lokaler Befehl

```bash
python3 tools/check_wordpress_bridge_php_syntax.py
```

## Regeln

- Wenn `php` fehlt, ist der Gate `tooling_missing`.
- Wenn `php -l` fuer alle Plugin-Dateien gruen ist, ist der Gate `passed`.
- Wenn eine Datei fehlschlaegt, ist der Gate `failed`.
- Ohne gruenes Ergebnis darf keine neutrale 10/10-Produktionsbewertung behauptet werden.

## Status

- Gate Definition: `implemented_locally`
- Current Environment: `tooling_missing_until_php_cli_available`
