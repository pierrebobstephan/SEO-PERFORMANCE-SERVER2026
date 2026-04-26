# Staging Pilot Installation Flow

## Ablauf

1. Backup bestaetigen
2. Restore-Basis bestaetigen
3. Theme/Builder/SEO-Plugin-Inventar sichern
4. staging-only Pilotpaket installieren
5. Plugin in `observe_only` oder `safe_mode` aktivieren
6. erste Diagnostics pruefen
7. Stop-/Rollback-Kriterien gegenpruefen

## Nicht erlaubt

- direkt in aktive Ausgabe wechseln
- anderes SEO-Plugin deaktivieren
- protected delivery oeffentlich freigeben

## Gate

- Staging Pilot Installation Flow: `approval_required`
