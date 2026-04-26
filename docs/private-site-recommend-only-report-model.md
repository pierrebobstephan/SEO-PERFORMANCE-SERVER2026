# Private Site Recommend-Only Report Model

## Zweck

Dieser Report prueft freigegebene oeffentliche Seiten auf der privaten Ziel-Domain innerhalb des aktuellen `recommend_only`-Rahmens.

## Scope

- Root-Domain `electri-c-ity-studios-24-7.com`
- Homepage
- About Us
- Impressum
- Privacy Policy

## Guardrails

- keine Live-Uebernahme durch die Bridge
- keine Rank-Math-Ablosung
- keine globale Site-Manipulation
- keine Oeffnung geschuetzter Routen
- nur bounded Diagnostics und Empfehlungen

## Output

- JSON: `var/reports/private-site/electri-city-root-recommend-only.latest.json`
- Markdown: `var/reports/private-site/electri-city-root-recommend-only.latest.md`

## Innovationsschicht

- `innovation_control_deck`
  - gemeinsame Operator-Zusammenfassung fuer Ausfuehrungsmodus, Prioritaetsfokus, sichere Sofortschritte, naechste Innovationsschritte, Erfolgssignale und geschuetzte Holds
- `priority_execution_queue`
  - priorisierte Seiten-Queue mit `priority`, `focus`, `why_now` und `top_actions`
- `automation_candidates`
  - nur fuer eng gefasste, admin-bestaetigte Assisted-Resolution-Schritte
  - aktueller Scope: Rank-Math-Meta-Description-Updates mit Before-State-Capture und Rollback-Bereitschaft
- Ziel:
  - aus reinen Fundstellen eine kontrollierte, buyer-readable Handlungsschicht machen
  - `recommend_only` staerken, ohne Live-Ownership oder Delivery-Freigaben zu oeffnen

## Assisted Resolution Lane

- `execution_lane = admin_confirmed_assisted_resolution_only`
- keine Bridge-Live-Ownership
- Aenderung erfolgt nur im bestehenden SEO-Owner
- nur nach expliziter Admin-Bestaetigung
- nur mit captured before-state, Validierungschecks und Rueckrollpfad

## Automation Contract Gate

- Contract Registry: `config/automation-contracts.json`
- Default Policy: `deny_by_default`
- Kandidaten werden nur erzeugt, wenn die Registry gueltig ist
- Kandidaten muessen Runtime-Gate, aktiven SEO-Owner, Target Field und Exact-Domain-Bindung gegen den Vertrag erfuellen
- aktueller einziger Contract: `ac-rank-math-meta-description-update-v1`
- alle anderen Vorschlaege bleiben reine Report-Empfehlungen ohne Apply-Lane
- das private Root-Domain-Paket kann einen gebuendelten Snapshot unter `config/private-site-report.latest.json` enthalten, falls die WordPress-PHP-Laufzeit den absoluten Suite-Report-Pfad nicht lesen darf

## Email

- Empfaenger: `pierre.stephan1@outlook.com`
- SMTP-Profil: `ionos_starttls_submission`
- Secrets nur ueber Env-Refs
