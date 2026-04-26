# Pilot Readiness Checklist

## Zweck

Diese Checkliste prueft vor jedem spaeteren Pilot, ob die bindende Doktrin aus [AGENTS.md](/opt/electri-city-ops/AGENTS.md), [docs/system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md), [Doktrin04.04.2026-Version-8.0.txt](/opt/electri-city-ops/Doktrin04.04.2026-Version-8.0.txt) und [docs/doctrine-alignment-report.md](/opt/electri-city-ops/docs/doctrine-alignment-report.md) eingehalten wird.

## Doktrinischer Pflichtcheck

- Ist der geplante Schritt mit [AGENTS.md](/opt/electri-city-ops/AGENTS.md) konsistent?
- Ist der geplante Schritt mit [docs/system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md) konsistent?
- Ist der geplante Schritt mit der 8.0-Quellfassung [Doktrin04.04.2026-Version-8.0.txt](/opt/electri-city-ops/Doktrin04.04.2026-Version-8.0.txt) konsistent?
- Bleibt `observe_only`, `safe_mode` oder `approval_required` aktiv, solange Inputs oder Freigaben fehlen?
- Gibt es keinerlei Wirkung ausserhalb `/opt/electri-city-ops`, solange kein Pilot freigegeben ist?
- Ist Rocket Cloud vollstaendig unangetastet?

## AI-Management-Check

- Gibt es einen Registereintrag fuer das betroffene System?
- Ist eine Risikoklasse `R0` bis `R4` gesetzt?
- Liegt ein Impact-Assessment oder ein sauberer Assessment-Verweis vor?
- Sind Human Oversight und Eskalationswege geklaert?
- Sind Provenance- und Supply-Chain-Annahmen dokumentiert?

## Gate-Check

- Ist ein klarer Connector-Typ festgelegt?
- Ist der Ziel-Scope klein und eindeutig?
- Ist der aktuelle Gate-Status dokumentiert?
- Wuerde der Schritt bei Unsicherheit auf `observe_only`, `safe_mode`, `approval_required` oder `blocked` fallen?

## Sicherheits-Check

- Ist der Blast Radius klein?
- Ist der Rueckweg klar und dokumentiert?
- Sind keine OS-, Service-, Scheduler- oder Fremdsystemeingriffe beteiligt?
- Sind keine globalen oder unklar begrenzten Regeln vorgesehen?
- Ist `fail closed` bei Unsicherheit gewaehrleistet?

## Validation- und Evidence-Check

- Existiert eine Vorher-Messung?
- Existieren Primaermetriken und Nachbarsignale?
- Sind Abort- und Rollback-Kriterien definiert?
- Ist ein Simulationsobjekt mit `risk_class`, `impact_assessment_ref`, `evidence_plan` und `aftercare_window` vorhanden?
- Ist erklaerbar, warum gerade diese Massnahme und keine aggressivere Alternative gewaehlt wird?

## Ergebnislogik

Setze `pilot_ready` nur wenn alle Pflichtchecks positiv beantwortet sind.

Setze `approval_required`, wenn:

- Freigaben fehlen
- Secrets fehlen
- Connector oder Zielbereich noch nicht bestaetigt sind
- Assessment-, Provenance- oder Ownership-Daten fehlen

Setze `blocked`, wenn:

- kein klarer Rollback existiert
- der Blast Radius zu gross ist
- der Zielscope unklar ist
- die Massnahme gegen [AGENTS.md](/opt/electri-city-ops/AGENTS.md), [docs/system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md) oder [docs/doctrine-alignment-report.md](/opt/electri-city-ops/docs/doctrine-alignment-report.md) verstoesst
- die Massnahme gegen die 8.0-Quellfassung verstoesst
