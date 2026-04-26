# Promotion Decision To Reference Pilot

## Ziel

Erst nach bestandenem Real-Staging-Test darf ein streng kontrollierter Referenzpilot ueberhaupt erwogen werden.

## Voraussetzung

- URL-Normalisierung bestanden
- staging-only Install und Safe-Mode-Test bestanden
- Rollback Drill bestanden
- Coexistence-Lage klar
- Scope bleibt eng

## Entscheidung

- go to reference pilot: nur bei komplett gruener Evidenz
- stay in staging: bei unklarer Coexistence oder fehlender Evidenz
- rollback and redesign: bei Seitenschaeden, Ownership-Problemen oder Scope-Risiko

## Gate

- Promotion Decision To Reference Pilot: `approval_required`
