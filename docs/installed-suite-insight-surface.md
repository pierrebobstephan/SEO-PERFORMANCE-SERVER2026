# Installed Suite Insight Surface

## Zweck

- dem Kaeufer oder Operator nach Installation klar zeigen:
  - was gebunden und erkannt wurde
  - was aktuell sicher beobachtet werden darf
  - was weiter geschuetzt bleibt
  - welche Daten noch fehlen
  - warum die Suite noch in `observe_only`, `safe_mode`, `recommend_only` oder spaeter `reversible_change_ready` steht

## Keine Freigabe dadurch

- kein Customer-Login
- keine offene Download-Ausgabe
- keine Produktionsfreigabe
- keine automatische Scope-Ausweitung

## Pflichtfelder

- Domain Binding
- Optimization Eligibility
- Innovation Control Deck
- Open Blockers
- Resolved Blockers
- Operator Inputs
- Source Mapping Status
- Safe Now
- What Stays Protected
- Customer Subscription Visibility
- Protected Delivery Status
- buyer-readable Explainability- und Trust-Signale

## Innovationsschicht

- Das Plugin soll nicht nur Rohstatus zeigen, sondern eine klare operator-taugliche Steuerlage:
  - Ausfuehrungsmodus
  - Prioritaetsfokus
  - Immediate Safe Actions
  - Next Innovation Actions
  - Success Signals
  - Protected Holds
- Diese Schicht oeffnet keine neue Live-Wirkung; sie macht die bestehende Guardrail-Lage nur handlungsfaehiger und nachvollziehbarer.

## Assisted Resolution Lane

- Wenn ein lokaler Suite-Report eine eng gefasste Automationsmoeglichkeit liefert, darf das Plugin eine `Recommendation Action Center`-Schicht zeigen.
- Diese Lane bleibt:
  - admin-bestaetigt
  - rollback-first
  - nur innerhalb des aktiven SEO-Owners
  - ohne Bridge-Live-Ownership
  - ohne Oeffnung von Delivery-, Login- oder Public-Routen

## Contract-Gate fuer assistierte Aktionen

- Das Plugin akzeptiert keine Report-Kandidaten ohne `automation_contract_id`, `automation_contract_version` und `automation_contract_state = contract_verified`.
- Der lokale Report erzeugt Kandidaten nur bei gueltiger `deny_by_default`-Registry.
- Der aktuelle Contract erlaubt ausschliesslich `rank_math_meta_description_update` fuer `rank_math_description`.
- Runtime muss weiter `recommend_only`, domain-bound und Rank-Math-koexistent sein.
- Jede Ausfuehrung braucht Admin-Bestaetigung, Before-State-Capture, Post-Write-Validierung und Rollback-Journal.
- Wenn die WordPress-PHP-Laufzeit den absoluten Suite-Report-Pfad nicht lesen kann, darf das private Paket einen paketlokalen Snapshot unter `config/private-site-report.latest.json` als Fallback nutzen.
