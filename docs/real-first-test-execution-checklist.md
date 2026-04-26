# Real First Test Execution Checklist

## Vor Installation

- [ ] URL-Normalisierung bestaetigt
- [ ] Backup bestaetigt
- [ ] Restore bestaetigt
- [ ] Rollback Owner benannt
- [ ] Validation Owner benannt
- [ ] Theme/Builder/SEO-Plugin-Inventar dokumentiert

## Installation

- [ ] staging-only Paket hochgeladen
- [ ] Plugin-Version `0.1.0-real-staging1` bestaetigt
- [ ] Aktivierung gestartet
- [ ] Startmodus `safe_mode` oder `observe_only` bestaetigt

## Erste Validierung

- [ ] `/wordpress/` laedt ohne sichtbaren Schaden
- [ ] `/wordpress/beispiel-seite/` laedt ohne sichtbaren Schaden
- [ ] keine doppelte Head-/Meta-Ausgabe sichtbar
- [ ] Konflikte bleiben beobachtbar
- [ ] Stop-Bedingungen nicht ausgeloest

## Falls noetig

- [ ] Rollback ausgelost
- [ ] Vorher-Zustand wiederhergestellt

## Gate

- Real First Test Execution Checklist: `approval_required`
