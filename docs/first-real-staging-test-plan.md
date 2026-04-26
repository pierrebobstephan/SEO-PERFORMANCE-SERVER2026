# First Real Staging Test Plan

## Ziel

Der erste echte kontrollierte Test der Suite soll ausschliesslich auf einer staging-/testfaehigen WordPress-Umgebung vorbereitet werden.

## Testrahmen

- nur staging domain oder staging subdomain
- exakte licensed test domain
- Backup vor Installation zwingend
- Restore und Rollback vor Installation zwingend
- Plugin startet in `observe_only` oder `safe_mode`
- erster Scope bleibt auf Homepage Meta / Head / Structure / visibility diagnostics begrenzt

## Mindestablauf

1. Testdomain und Lizenz-Scope bestaetigen
2. Backup- und Restore-Bestaetigung einholen
3. Theme/Builder/SEO-Plugin-Inventar sichern
4. Plugin staging-only installieren
5. Plugin in `observe_only` oder `safe_mode` aktivieren
6. Observe-only Diagnostik pruefen
7. Stop-/Rollback-Kriterien gegenpruefen

## Gate

- First Real Staging Test Plan: `approval_required`
