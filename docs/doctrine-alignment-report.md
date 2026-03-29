# Doctrine Alignment Report

## Zweck

Dieser Bericht spiegelt die neue Oberdoktrin aus [AGENTS.md](/opt/electri-city-ops/AGENTS.md) und [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md) gegen die bereits vorhandenen Architektur-, Gate-, Validation-, Rollback- und Observe-only-Dokumente.

## Bereits konsistente Dokumente

### Verbindliche Repo-Doktrin

- [AGENTS.md](/opt/electri-city-ops/AGENTS.md)
- [system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md)

Konsistent, weil:

- die eingehenden Fassungen fachlich aufgenommen und repo-konform integriert wurden
- die kanonische Langfassung und die knappe Repo-Steuerung nun dieselbe Oberdoktrin tragen
- observe_only, Connector-Zwang, Validierung, Rollback und Betriebssystemschutz explizit gemeinsam verankert sind

### Architektur und Zielbild

- [master-architecture-phase-3-5.md](/opt/electri-city-ops/docs/master-architecture-phase-3-5.md)
- [architecture.md](/opt/electri-city-ops/docs/architecture.md)

Konsistent, weil:

- Autonomie nur innerhalb harter Grenzen gedacht ist
- Beobachtung, Planung, Freigabe, Anwendung, Validierung und Lernen klar getrennt werden
- Betriebssystem-, Workspace- und Fremdsystemschutz explizit priorisiert sind

### Gate-, Validation- und Rollback-Logik

- [approval-gate-spec.md](/opt/electri-city-ops/docs/approval-gate-spec.md)
- [validation-engine-spec.md](/opt/electri-city-ops/docs/validation-engine-spec.md)
- [rollback-playbooks.md](/opt/electri-city-ops/docs/rollback-playbooks.md)
- [decision-model.md](/opt/electri-city-ops/docs/decision-model.md)

Konsistent, weil:

- externe Wirkung nur ueber Freigabe und definierte Zustaende gedacht ist
- `rollback_required` als Pflichtreaktion auf fehlerhafte Wirkung vorgesehen ist
- Nachbarsignale und Vorher/Nachher-Vergleich die defensive Schutzlogik stuetzen

### Observe-only und datengetriebener Ausbau

- [observe-only-expansion-plan.md](/opt/electri-city-ops/docs/observe-only-expansion-plan.md)
- [operations.md](/opt/electri-city-ops/docs/operations.md)
- [data-model-roadmap.md](/opt/electri-city-ops/docs/data-model-roadmap.md)

Konsistent, weil:

- `observe_only` als sicherer Default-Fallback bereits verankert ist
- die Datentiefe vor aktiver Optimierung bewusst ausgebaut werden soll
- Lernen auf Historie, Trends und defensiver Interpretation basiert

### Connector- und Change-Blueprints

- [cloudflare-connector-blueprint.md](/opt/electri-city-ops/docs/cloudflare-connector-blueprint.md)
- [wordpress-connector-blueprint.md](/opt/electri-city-ops/docs/wordpress-connector-blueprint.md)
- [change-blueprints-priority-1-5.md](/opt/electri-city-ops/docs/change-blueprints-priority-1-5.md)
- [phase-4-execution-blueprint.md](/opt/electri-city-ops/docs/phase-4-execution-blueprint.md)
- [wordpress-plugin-execution-strategy.md](/opt/electri-city-ops/docs/wordpress-plugin-execution-strategy.md)
- [plugin-connector-priority-shift.md](/opt/electri-city-ops/docs/plugin-connector-priority-shift.md)
- [plugin-pilot-candidate-1.md](/opt/electri-city-ops/docs/plugin-pilot-candidate-1.md)
- [plugin-minimal-input-list.md](/opt/electri-city-ops/docs/plugin-minimal-input-list.md)
- [product-platform-strategy.md](/opt/electri-city-ops/docs/product-platform-strategy.md)
- [license-and-domain-binding-model.md](/opt/electri-city-ops/docs/license-and-domain-binding-model.md)
- [plugin-distribution-and-update-model.md](/opt/electri-city-ops/docs/plugin-distribution-and-update-model.md)
- [customer-site-optimization-model.md](/opt/electri-city-ops/docs/customer-site-optimization-model.md)
- [reference-site-vs-customer-sites.md](/opt/electri-city-ops/docs/reference-site-vs-customer-sites.md)
- [license-object-spec.md](/opt/electri-city-ops/docs/license-object-spec.md)
- [plugin-activation-flow.md](/opt/electri-city-ops/docs/plugin-activation-flow.md)
- [update-manifest-model.md](/opt/electri-city-ops/docs/update-manifest-model.md)
- [plugin-bootstrap-architecture.md](/opt/electri-city-ops/docs/plugin-bootstrap-architecture.md)
- [local-plugin-safe-mode-spec.md](/opt/electri-city-ops/docs/local-plugin-safe-mode-spec.md)
- [plugin-conflict-detection-model.md](/opt/electri-city-ops/docs/plugin-conflict-detection-model.md)
- [release-channel-model.md](/opt/electri-city-ops/docs/release-channel-model.md)
- [plugin-mvp-implementation-plan.md](/opt/electri-city-ops/docs/plugin-mvp-implementation-plan.md)
- [plugin-module-map.md](/opt/electri-city-ops/docs/plugin-module-map.md)
- [plugin-admin-ui-model.md](/opt/electri-city-ops/docs/plugin-admin-ui-model.md)
- [plugin-license-status-model.md](/opt/electri-city-ops/docs/plugin-license-status-model.md)
- [plugin-homepage-meta-module-spec.md](/opt/electri-city-ops/docs/plugin-homepage-meta-module-spec.md)
- [plugin-rank-math-coexistence-model.md](/opt/electri-city-ops/docs/plugin-rank-math-coexistence-model.md)
- [control-plane-plugin-handshake.md](/opt/electri-city-ops/docs/control-plane-plugin-handshake.md)
- [license-check-api-contract.md](/opt/electri-city-ops/docs/license-check-api-contract.md)
- [plugin-policy-fetch-model.md](/opt/electri-city-ops/docs/plugin-policy-fetch-model.md)
- [plugin-update-check-flow.md](/opt/electri-city-ops/docs/plugin-update-check-flow.md)
- [domain-scoped-rollback-distribution.md](/opt/electri-city-ops/docs/domain-scoped-rollback-distribution.md)
- [reference-site-pilot-vs-customer-rollout.md](/opt/electri-city-ops/docs/reference-site-pilot-vs-customer-rollout.md)
- [customer-onboarding-minimal-flow.md](/opt/electri-city-ops/docs/customer-onboarding-minimal-flow.md)
- [phases-7-8-9-implementation-summary.md](/opt/electri-city-ops/docs/phases-7-8-9-implementation-summary.md)
- [open-inputs-before-live-productization.md](/opt/electri-city-ops/docs/open-inputs-before-live-productization.md)
- [approval-boundaries-before-real-deployment.md](/opt/electri-city-ops/docs/approval-boundaries-before-real-deployment.md)
- [control-plane-backend-core.md](/opt/electri-city-ops/docs/control-plane-backend-core.md)
- [license-registry-model.md](/opt/electri-city-ops/docs/license-registry-model.md)
- [policy-registry-model.md](/opt/electri-city-ops/docs/policy-registry-model.md)
- [manifest-builder-model.md](/opt/electri-city-ops/docs/manifest-builder-model.md)
- [rollback-profile-registry.md](/opt/electri-city-ops/docs/rollback-profile-registry.md)
- [domain-onboarding-registry-model.md](/opt/electri-city-ops/docs/domain-onboarding-registry-model.md)
- [backend-state-machine.md](/opt/electri-city-ops/docs/backend-state-machine.md)
- [plugin-packaging-model.md](/opt/electri-city-ops/docs/plugin-packaging-model.md)
- [release-artifact-model.md](/opt/electri-city-ops/docs/release-artifact-model.md)
- [operator-release-runbook.md](/opt/electri-city-ops/docs/operator-release-runbook.md)
- [operator-license-issuance-runbook.md](/opt/electri-city-ops/docs/operator-license-issuance-runbook.md)
- [operator-customer-onboarding-runbook.md](/opt/electri-city-ops/docs/operator-customer-onboarding-runbook.md)
- [dry-run-customer-rollout-model.md](/opt/electri-city-ops/docs/dry-run-customer-rollout-model.md)
- [live-productization-gates.md](/opt/electri-city-ops/docs/live-productization-gates.md)
- [domain-package-entitlement-model.md](/opt/electri-city-ops/docs/domain-package-entitlement-model.md)

Konsistent, weil:

- keine Anwendung ohne Freigabe, Validierung und Rollback vorgesehen ist
- Ziel-Connectoren klar getrennt sind
- Risiken und Rueckwege bereits als Pflichtbestandteile formuliert sind
- der Strategiewechsel den Hetzner-Stack nicht aus `observe_only` herauszieht, sondern nur den spaeteren primaeren Umsetzungspfad auf WordPress-Plugin verschiebt
- das Produktmodell jetzt explizit zwischen Referenzsystem, Kunden-Domains, Lizenzbindung und domaingebundener Wirkung trennt
- der Produktkern jetzt als lokale Spezifikationsschicht fuer Lizenzobjekt, Aktivierung, Bootstrap, Safe-Mode, Konflikterkennung, Manifest und Release-Kanaele vorliegt
- das lokale Plugin-MVP jetzt technisch nur inert startet und ohne bestaetigte Lizenz-, Policy-, Konflikt-, Validation- und Rollback-Lage keine aktive Ausgabe erzeugt
- der Control-Plane-Handshake jetzt lokal ueber domaingebundene Vertragsobjekte, Schemas und Fallback-Logik vorbereitet ist
- der Backend-Core jetzt lokale Registries fuer Lizenz, Policy, Rollback und Onboarding mit klaren Preconditions modelliert
- Packaging, Release-Artefakte, Entitlements und Operator-Runbooks jetzt nur als lokale Preview- und Dry-Run-Schicht vorliegen

### Pilotvorbereitung

- [pilot-candidate-1.md](/opt/electri-city-ops/docs/pilot-candidate-1.md)
- [pilot-candidate-2.md](/opt/electri-city-ops/docs/pilot-candidate-2.md)
- [pilot-readiness-checklist.md](/opt/electri-city-ops/docs/pilot-readiness-checklist.md)
- [pilot-simulation-template.md](/opt/electri-city-ops/docs/pilot-simulation-template.md)
- [missing-secrets-and-approvals.md](/opt/electri-city-ops/docs/missing-secrets-and-approvals.md)

Konsistent, weil:

- alle aktuellen Piloten weiter auf `approval_required` oder striktem Observe-only-Pfad bleiben
- die bindenden Referenzen auf AGENTS, kanonische Langfassung und Alignment-Report explizit sind
- `simulate` und `adapt` fuer Pilotvorbereitung jetzt als eigene Pflichtbestandteile dokumentiert sind

### Technische Doctrine-Enforcement-Schicht

- [doctrine-enforcement-plan.md](/opt/electri-city-ops/docs/doctrine-enforcement-plan.md)
- [policy-schema.md](/opt/electri-city-ops/docs/policy-schema.md)
- [runtime-guardrails.md](/opt/electri-city-ops/docs/runtime-guardrails.md)
- [pilot-gate-check-spec.md](/opt/electri-city-ops/docs/pilot-gate-check-spec.md)

Konsistent, weil:

- die Doktrin jetzt lokal ueber Policy-, Scope-, Blast-Radius-, Approval- und Rollback-Pruefungen technisch eingebunden ist
- externe Wirkung weiterhin technisch gesperrt bleibt und nur als `approval_required`, `blueprint_ready` oder `observe_only` modelliert wird
- Simulationsobjekte und Gate-Checks jetzt nicht nur dokumentiert, sondern lokal testbar spezifiziert sind

### Lokale Produktkern-, Plugin- und Vertragsartefakte

- `config/release-channels.json`
- `schemas/domain-binding.schema.json`
- `schemas/license-object.schema.json`
- `schemas/update-manifest.schema.json`
- `schemas/license-check-response.schema.json`
- `schemas/plugin-policy-response.schema.json`
- `schemas/rollback-profile.schema.json`
- `schemas/customer-domain-onboarding.schema.json`
- `src/electri_city_ops/product_core.py`
- `src/electri_city_ops/contracts.py`
- `packages/wp-plugin/hetzner-seo-ops/hetzner-seo-ops.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-plugin.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-license-check.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-safe-mode.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-conflict-detector.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-rollback-registry.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-validation-status.php`
- `packages/wp-plugin/hetzner-seo-ops/includes/modules/class-hso-meta-description-module.php`
- `packages/wp-plugin/hetzner-seo-ops/admin/class-hso-admin-screen.php`
- `tests/test_product_core.py`
- `tests/test_contracts.py`
- `config/backend-defaults.json`
- `schemas/license-registry-entry.schema.json`
- `schemas/policy-registry-entry.schema.json`
- `schemas/manifest-build-request.schema.json`
- `schemas/rollback-profile-entry.schema.json`
- `schemas/domain-onboarding-entry.schema.json`
- `schemas/plugin-package-metadata.schema.json`
- `schemas/release-artifact.schema.json`
- `schemas/domain-entitlement.schema.json`
- `src/electri_city_ops/backend_core.py`
- `src/electri_city_ops/registry.py`
- `src/electri_city_ops/manifest_builder.py`
- `src/electri_city_ops/rollback_registry.py`
- `src/electri_city_ops/onboarding.py`
- `tools/build_plugin_package.py`
- `tools/build_release_artifacts.py`
- `tools/dry_run_onboarding.py`
- `tests/test_backend_core.py`
- `tests/test_release_workflows.py`

Konsistent, weil:

- Domain-, Scope-, Kanal-, Policy- und Rollback-Bindung jetzt nicht nur beschrieben, sondern lokal validierbar modelliert sind
- das Plugin-MVP standardmaessig `observe_only`, `safe_mode` oder `approval_required` bleibt
- Rank Math koexistierend behandelt wird und keine abrupte Ablosung erzwungen wird
- fehlende Vertragsobjekte oder unklare Source-Mapping-Lagen technisch auf sichere Fallbacks ziehen
- Backend-Registry, Manifest-Build, Rollback-Lookup, Dry-Run-Onboarding und Live-Gates jetzt lokal testbar an klaren Preconditions haengen
- Packaging- und Release-Tools nur lokale Preview-Artefakte vorbereiten und keine echte Auslieferung kennen

Verifikationsstand:

- Python-Tests fuer Produktkern und Vertragslogik laufen lokal gruen
- Python-Tests fuer Backend-Core und Release-Workflows laufen lokal gruen
- `validate-config` bleibt doctrine-konform in `observe_only` mit `allow_external_changes = false`
- `compileall` fuer `src` und `tools` laeuft lokal durch
- PHP-Lint konnte mangels lokal installiertem `php` nicht ausgefuehrt werden

## Noch bestehende Luecken

### Erweiterte Gate-Zustaende sind noch nicht vollstaendig in Spezifikationen gespiegelt

Status:

- Die erweiterte Doktrin nennt zusaetzlich `local_safe_self_heal`, `active_pilot`, `stable_applied` und `degraded_safe`.

Luecke:

- [approval-gate-spec.md](/opt/electri-city-ops/docs/approval-gate-spec.md) spiegelt aktuell nur einen engeren Teil dieser Zustandslandschaft.

### Simulations- und Adaptionsschritt sind in Piloten jetzt explizit, aber noch nicht ueberall systemweit

Status:

- Die uebernommene Doktrin staerkt den Zyklus `observe -> analyze -> decide -> simulate -> apply -> validate -> learn -> adapt -> document`.

Restluecke:

- nicht alle aelteren Blueprint- oder Connector-Dokumente modellieren `simulate` und `adapt` bereits als eigene, explizite Phasen.

### Dokumentationspflicht ist kanonisch staerker als in einzelnen Spezifikationen

Status:

- Die neue Doktrin fordert ein sehr explizites Pflichtschema fuer Kontext, Scope, Hypothese, Nebeneffekte, Rollback und finalen Status.

Luecke:

- einige Phase-4- und Phase-5-Dokumente beschreiben diese Punkte inhaltlich, aber noch nicht als einheitliches Pflicht-Datenobjekt.

### Modulbindung an die Doktrin ist lokal begonnen, aber fuer reale Connector-Laufzeiten noch nicht vollstaendig

Status:

- Die Doktrin ist jetzt lokal in Policies, Schemas, Runtime-Checks und Tests verankert.

Restluecke:

- Eine spaetere Umsetzung muss dieselbe Durchsetzung noch direkt an reale Cloudflare-, WordPress- oder andere Connector-Laufzeiten koppeln, sobald solche Pfade ueberhaupt freigegeben werden.

### Plugin-MVP ist lokal modelliert, aber noch nicht gegen echte WordPress-Laufzeitmatrix validiert

Status:

- Das Plugin-Skeleton ist lokal vorhanden und php-lintbar geplant.

Restluecke:

- echte WordPress-Integrations- und Kompatibilitaetstests gegen konkrete Themes, Builder und Rank-Math-Varianten sind bewusst noch nicht freigegeben.

### Vertragsobjekte sind lokal formalisiert, aber noch nicht kryptographisch oder transportseitig abgesichert

Status:

- License-, Policy- und Rollback-Antworten sind lokal als Schemas und Python-Validatoren modelliert.

Restluecke:

- Signaturmodell, Transportabsicherung, Replay-Schutz und reale Secret-Verwaltung bleiben vor echter Produktisierung `approval_required`.

### Backend-Core und Packaging sind lokal modelliert, aber noch nicht an echte Operator- oder Auslieferungsrealitaet gebunden

Status:

- Registries, Manifest-Builder, Entitlements, Dry-Run-Tools und Release-Preview-Artefakte sind lokal vorhanden.

Restluecke:

- echte Lizenz-Registry, reale Policy-Verteilung, reale Download-Freigabe, Upload-Pfade und Operator-Four-Eyes-Freigaben bleiben vor Produktisierung `approval_required`.

### Wissensaustausch ist architektonisch beschrieben, aber noch nicht maximal explizit pro Modulfluss

Status:

- Modulkooperation ist in Architektur- und Modulplandokumenten vorhanden.

Luecke:

- Spaetere Spezifikationen koennen die konkreten Datenvertraege zwischen trend_engine, learning_engine, change_planner, validation_engine und reporting_engine noch staerker formalisieren.

## Module, die besonders streng an AGENTS.md und system-doctrine.md gebunden sein muessen

### approval_gate

- weil hier entschieden wird, ob Beobachtung, Freigabe, Pilot oder Blockade gilt

### validation_engine

- weil hier gemessen wird, ob eine Wirkung akzeptabel, gemischt oder rueckzunehmen ist

### rollback-Mechanik

- weil sie die letzte Schutzbarriere gegen fehlerhafte oder riskante Wirkung darstellt

### change_planner

- weil hier aus Beobachtung spaetere Wirkung wird und Scope, Risiko und Reversibilitaet korrekt modelliert werden muessen

### learning_engine

- weil Lernen nie zu aggressiver oder schlecht erklaerbarer Autonomie fuehren darf

### Cloudflare- und WordPress-Connectoren

- weil diese spaeter die reale externe Wirkung erzeugen koennen und deshalb strikt an Workspace-Grenzen, Freigabe, Validation und Rollback gebunden bleiben muessen

### plugin bootstrap, conflict detection und meta description module

- weil hier im spaeteren Produkt die erste lokale Wirkung auf der Kunden-Domain entstehen koennte und deshalb Safe-Mode, Scope-Klarheit, Konfliktpruefung und Doppel-Ausgabe-Vermeidung strikt bleiben muessen

### product_core und contracts

- weil hier Lizenz-, Domain-, Kanal-, Policy- und Rollback-Bindung modelliert werden und jeder Fehler hier zu unklarer Mehrdomain- oder Mehrscope-Wirkung fuehren koennte

### backend_core, registry, manifest_builder, rollback_registry und onboarding

- weil hier die interne Produktautoritaet fuer Domain-Bindung, Policy-Verengung, Manifest-Preconditions, Rollback-Faehigkeit und Onboarding-Zustaende entsteht

### Packaging-, Release- und Entitlement-Schicht

- weil hier spaeter Download-Anspruch, Kanalbindung und Go-Live-Grenzen technisch vorbereitet werden und jede Aufweichung direkt zu unklarer Produktwirkung fuehren koennte

## Alignment-Fazit

Die bestehende Dokumentlandschaft ist inhaltlich weitgehend mit der neuen Doktrin vereinbar. Die neue Oberdoktrin schliesst vor allem die Luecke einer zentralen, verbindlichen Repo-Steuerung und einer kanonischen Langfassung fuer Autonomie, defensive Schutzlogik, Lernen, Selbstheilung und sichere Selbstoptimierung.

Fuer spaetere technische Umsetzung bleibt die wichtigste Folgeaufgabe:

- die nun lokal verankerte Doktrin spaeter mit denselben Guardrails an reale, ausdruecklich freigegebene Connector-Laufzeiten zu koppeln, ohne die Workspace- und Observe-only-Sicherheitsbasis aufzuweichen.
