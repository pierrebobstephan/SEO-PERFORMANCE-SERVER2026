# Real Staging Install Flow

## Reihenfolge

1. URL-Normalisierung pruefen
2. Backup bestaetigen
3. Restore bestaetigen
4. Plugin staging-only installieren
5. in `observe_only` oder `safe_mode` aktivieren
6. `/wordpress/` und `/wordpress/beispiel-seite/` inspizieren
7. bei Fatal Error, Doppel-Ausgabe, Ownership-Unklarheit oder sichtbarem Schaden abbrechen

## Gate

- Real Staging Install Flow: `approval_required`
