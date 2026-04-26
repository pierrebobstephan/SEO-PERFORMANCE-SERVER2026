# Bridge Plugin Safe Boot Sequence

## Reihenfolge

1. packaged bridge config laden
2. domain binding pruefen
3. conflict snapshot erfassen
4. baseline snapshot erfassen
5. validation snapshot bauen
6. optimization eligibility berechnen
7. nur wenn alle Guardrails sauber sind, reversible Stage-1-Vorbereitung erlauben

## Harte Fallbacks

- domain mismatch -> `observe_only`
- url normalization not clean -> `safe_mode`
- blocking conflict -> `safe_mode`
- unklare source ownership -> `approval_required`

## Gate

- Bridge Plugin Safe Boot Sequence: `approval_required`
