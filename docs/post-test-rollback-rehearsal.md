# Post-Test Rollback Rehearsal

## Ziel

Rollback soll nach dem Test nicht nur dokumentiert, sondern durchgesprochen und pruefbar reproduzierbar sein.

## Rehearsal

1. Rueckbau des Plugins oder Rueckkehr in `observe_only`
2. Kontrollblick auf Head-/Meta-/Structure-Signale
3. Vergleich gegen Before-State
4. Dokumentation des Rehearsal-Ergebnisses

## Pflicht

- kein bestandenes Testfazit ohne intakten Rollback-Rehearsal-Pfad

## Gate

- Post-Test Rollback Rehearsal: `approval_required`
