# Source Mapping Confirmation Runbook

## Ziel

- die Ownership der Homepage-Meta-/Head-Ausgabe explizit bestaetigen

## Ablauf

1. `Site Optimizer` im WordPress Admin oeffnen
2. Bereich `Source Mapping Confirmation` pruefen
3. bestaetigen:
   - Homepage Meta Description ist single-source
   - Head/Meta Output ist single-source
   - Duplicate Output wurde nicht gefunden
   - bei aktivem Rank Math: Rank Math bleibt aktuelle Live-Quelle, die Bridge uebernimmt noch keine Live-Ausgabe
4. Operator-Bestaetigung setzen
5. Notizen speichern
6. Nach Redirect pruefen:
   - `source_mapping_confirmed`
   - `open_blockers`
   - `optimization gate status`
   - `coexistence_mode`

## Stop

- bei doppelter Ausgabe
- bei unklarer Ownership
- bei neuer Konfliktlage
