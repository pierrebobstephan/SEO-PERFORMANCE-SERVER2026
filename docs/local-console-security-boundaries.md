# Local Console Security Boundaries

## Zweck

Dieses Dokument beschreibt die Sicherheitsgrenzen der lokalen Browser-Konsole.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Die Konsole ist lokal-only und whitelisted.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede Abweichung von localhost-only waere `approval_required`.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Prozess stoppen, keine Bindung ausserhalb `127.0.0.1`.

## Harte Grenzen

- Standard-Bindung nur an `127.0.0.1`
- keine Bindung an `0.0.0.0` als Default
- keine echte API nach aussen
- keine Login- oder Customer-Live-Funktion
- keine Connector-Schreibzugriffe
- keine WordPress-, Cloudflare-, systemd-, cron- oder Notification-Aktivierung

## Action-Sicherheit

- nur feste lokale Whitelist
- keine frei eingegebenen Shell-Befehle
- keine Parameter, die externe Ziele oeffnen
- nur lokale Tests, lokale Config-Checks und lokale Preview-Builds

## Status

- Sicherheitsgrenzen: `blueprint_ready`
- jede oeffentliche Freigabe: `blocked` bis explizite Neudefinition
