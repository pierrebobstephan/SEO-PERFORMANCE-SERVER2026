# Duplicate Head Meta Detection Model

## Ziel

Duplicate Head-/Meta-Output soll nicht mehr als Black-Box-Blocker wirken.

## Zustaende

- `not_detected`
- `heuristic_suspected`
- `confirmed_runtime_output`

## Bedeutung

- `not_detected`: kein Duplicate-Signal vorhanden
- `heuristic_suspected`: es gibt einen Verdacht, aber noch keinen belastbaren Runtime-Nachweis
- `confirmed_runtime_output`: Duplicate-Output ist im gerenderten Output bestaetigt und bleibt ein realer Blocker

## Gate-Regel

- nur `confirmed_runtime_output` blockiert hart
- `heuristic_suspected` bleibt sichtbar, aber darf nicht als dauerhafter harter Blocker behandelt werden
