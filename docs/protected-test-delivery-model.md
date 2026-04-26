# Protected Test Delivery Model

## Ziel

Eine spaetere Testauslieferung darf nur geschuetzt, staging-only und ruecknehmbar stattfinden.

## Regeln

- keine oeffentliche Auslieferung
- keine offene Downloadseite
- keine Customer-Self-Service-Aktivierung
- Delivery nur fuer gebundene Testdomain und dokumentierten Testscope
- Safe Mode / Observe Only zuerst

## Validierung vor spaeterer Auslieferung

- Backup vorhanden
- Restore-Pfad bestaetigt
- Theme/Builder/SEO-Plugin-Inventar bekannt
- Rollback-Schritte dokumentiert

## Gate

- Protected Test Delivery: `approval_required`
