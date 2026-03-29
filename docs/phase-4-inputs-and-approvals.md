# Phase 4 Inputs and Approvals

## Welche Zugangsdaten und Freigaben spaeter konkret benoetigt werden

### Cloudflare

- freigegebene Zone
- API-Token mit minimalem Scope
- erlaubte Regeltypen
- Bestaetigung der erlaubten Pfade und Ausnahmen

### WordPress

- freigegebene Zielbereiche
- Information ueber Theme, Builder und SEO-Plugins
- Connector-Zugang oder anderer freigegebener Aenderungspfad
- Bestaetigung, ob nur Homepage oder weitere Seitentypen betroffen sein duerfen

### Observe-only

- keine Schreibrechte
- nur fortgesetzter read-only Zugriff auf die freigegebenen Ziel-Domains

## Was optional ist

- Search-Console-Zugang
- Analytics-Zugang
- CDN-Zusatzdaten
- spaetere Notification-Ziele
- spaetere Scheduler-Aktivierung

## Was zuerst benoetigt wird

Zuerst benoetigt fuer saubere Blueprint-Vervollstaendigung:

- Bestaetigung der spaeter erlaubten Connectoren
- Bestaetigung der Zielzonen und Zielbereiche
- Bestaetigung des gewuenschten Pilot-Scope
- Bestaetigung der Rollback-Verantwortung

## Was erst vor echter Anwendung benoetigt wird

- produktive API-Tokens
- produktive WordPress-Zugaenge
- verbindliche Betreiberfreigabe pro Change-Klasse
- konkrete Pilotfenster
- konkrete Rollback-Fenster

## Reihenfolge der Freigaben

1. Connector-Freigabe
2. Zielbereichs-Freigabe
3. Pilot-Scope-Freigabe
4. Validierungs- und Rollback-Freigabe
5. erst dann spaetere Anwendung

