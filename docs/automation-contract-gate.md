# Automation Contract Gate

## Zweck

Dieses Gate verhindert, dass Report-Fundstellen automatisch zu Plugin-Wirkung werden. Jede assistierte Aktion braucht einen expliziten lokalen Vertrag in `config/automation-contracts.json`.

## Default

- `default_policy = deny_by_default`
- unbekannte `action_type` wird nicht ausgegeben
- fehlende oder ungueltige Contract Registry erzeugt keine Kandidaten
- das Plugin fuehrt keine Kandidaten ohne passende Contract-ID, Version und `contract_verified` aus
- ein nicht lesbarer Report-Pfad erzeugt keine Wirkung; das private Paket darf einen gebuendelten, domaingebundenen Report-Snapshot als Fallback mitbringen

## Aktuell freigegebene Vertraege

- Contract: `ac-rank-math-meta-description-update-v1`
- Action type: `rank_math_meta_description_update`
- Risk class: `R1`
- Scope: `exact_domain_rank_math_post_meta_only`
- Execution lane: `admin_confirmed_assisted_resolution_only`
- Runtime gate: nur `recommend_only`
- Target field: nur `rank_math_description`
- SEO owner: nur `seo-by-rank-math/rank-math.php`

- Contract: `ac-rank-math-homepage-meta-description-update-v1`
- Action type: `rank_math_homepage_meta_description_update`
- Risk class: `R1`
- Scope: `exact_domain_rank_math_homepage_option_only`
- Execution lane: `admin_confirmed_assisted_resolution_only`
- Runtime gate: nur `recommend_only`
- Target field: nur `rank_math_titles.homepage_description`
- SEO owner: nur `seo-by-rank-math/rank-math.php`

## Preconditions

- Domain Binding ist gruen
- Operator Inputs sind vollstaendig
- Source Mapping ist bestaetigt
- Rank Math bleibt aktiver SEO Owner unter kontrollierter Koexistenz
- Ziel-URL liegt exakt auf der gebundenen Domain
- Homepage-Kandidaten muessen zusaetzlich exakt zur aktuellen WordPress-Homepage-URL passen

## Validierung

- Zielseite muss zu einer WordPress-Seite auf der lizenzierten Domain aufloesen
- Homepage-Kandidaten muessen zur aktuellen WordPress-Homepage aufloesen und schreiben ausschliesslich in die Rank-Math-Homepage-Option
- vorheriger Rank-Math-Wert wird vor dem Write erfasst
- gespeicherter Wert muss nach Apply exakt dem Vorschlag entsprechen
- keine Bridge-eigene Live-Output-Schicht wird durch diese Aktion aktiviert

## Rollback

- vorherigen `rank_math_description`-Wert wiederherstellen, wenn vorhanden
- temporaeren Wert loeschen, wenn vorher kein Wert vorhanden war
- vorherigen `rank_math_titles.homepage_description`-Wert wiederherstellen, wenn vorhanden
- temporaeren Homepage-Optionswert loeschen, wenn vorher kein Wert vorhanden war
- Journal-Eintrag als `rolled_back` markieren
- Rollback gilt erst nach erfolgreicher Nachvalidierung als abgeschlossen

## Geschuetzte Holds

- keine Rank-Math-Deaktivierung
- kein Bridge-eigener Live-Meta-Output
- kein globaler Head Rewrite
- kein Canonical Override
- keine Public Route Exposure

## Report-Ingest-Fallback

- Primaerquelle: `local_report_ingest.path`
- Private Paket-Fallback: `local_report_ingest.bundled_snapshot_path`
- Der Fallback liegt paketlokal unter `config/private-site-report.latest.json`
- Der Fallback wird nur akzeptiert, wenn `bound_domain` exakt zur Runtime-Domain passt
- Auch bei Fallback bleiben Admin-Bestaetigung, Before-State-Capture, Contract-Pruefung und Rollback Pflicht

## Doctrine 8.0 Einordnung

- Scope: lokale Root-Domain-Pilotinstallation und lokaler Report-Ingest
- Risikoklassifikation: `R1`, weil ein Admin-bestaetigter Write in WordPress-Post-Meta oder in die Rank-Math-Homepage-Option moeglich ist
- Validierungsdefinition: Contract-Validierung, Runtime-Gate, Exact-Domain-Bindung, Admin-Bestaetigung, Post-Write-Check
- Rollback-Plan: Before-State-Capture plus Plugin-Journal-Rollback
- Fallback: bei Unsicherheit, fehlendem Contract, Domain-Mismatch oder Runtime-Mismatch `deny_by_default`
