# Secret And Certificate Handling Plan

## Grundsatz

Zertifikate und Secrets werden getrennt von Workspace-Backups behandelt.

## Beispiele

- TLS-Zertifikate und Private Keys
- SMTP-Zugangsdaten
- spaetere Signatur- oder Lizenzschluessel
- spaetere API-Tokens

## Regeln

- keine Klartext-Secrets im Repo
- keine unverschluesselten Private Keys im Workspace
- echte `.env`-Dateien duerfen nicht versioniert oder in Workspace-Backups mitgesichert werden
- `.env.example`-Dateien duerfen nur Platzhalter enthalten
- lokale Governance blockiert Readiness, wenn sensible Env-Werte im Workspace gefunden werden
- Restore und Migration brauchen einen separaten Secret- und Zertifikatsplan

## Status

- Secret and Certificate Handling Plan: `implemented_locally`
- reale Secret- oder Zertifikatsrotation: `approval_required`
