# Real Staging Go / No-Go Checklist

## Zweck

Dieses Dokument ist die eine Operator-Checkliste fuer den letzten realen Staging-Pfad vor einer ehrlichen 10/10-Freigabe.

Es verdichtet diese bestehenden Unterlagen:

- `docs/ready-for-real-staging-test-gate.md`
- `docs/real-install-runbook.md`
- `docs/real-install-verification-pass.md`
- `docs/real-safe-mode-test-runbook.md`
- `docs/real-coexistence-pass.md`
- `docs/real-rollback-drill.md`
- `docs/promotion-decision-to-reference-pilot.md`

## Einsatzregel

- Kein Schritt wird als `GO` markiert, solange Evidence, Owner und Zeitpunkt fehlen.
- Ein einzelnes `NO-GO` auf einer Blocking-Stufe stoppt die Kette.
- Bei Unsicherheit gilt `NO-GO`, `rollback`, `redesign` oder `stay in staging`.

## Laufdaten

- Testdatum:
- Operator:
- Rollback Owner:
- Validation Owner:
- Bound Test Host: `wp.electri-c-ity-studios-24-7.com`
- Path Base: `/wordpress/`
- Expected Home URL: `https://wp.electri-c-ity-studios-24-7.com/wordpress/`
- Expected Scoped Page URL: `https://wp.electri-c-ity-studios-24-7.com/wordpress/beispiel-seite/`
- Install Package: `dist/staging-only/site-optimizer-bridge-0.1.0-real-staging1-wp-electri-c-ity-studios-24-7-com.zip`
- Package Metadata: `manifests/previews/final-real-staging-pilot-package-metadata.json`
- Manifest: `manifests/previews/final-real-staging-pilot-manifest-preview.json`
- Entitlement: `manifests/previews/final-real-staging-pilot-entitlement-preview.json`
- Rollback Profile: `manifests/previews/final-real-staging-pilot-rollback-profile-preview.json`

## Stage 0: Gate Vor Teststart

Status: `[ ] GO` `[ ] NO-GO`

- [ ] `localhost`-Reste vollstaendig beseitigt
- [ ] URL-Normalisierung sauber bestaetigt
- [ ] WordPress-Version dokumentiert
- [ ] aktives Theme dokumentiert
- [ ] aktiver Builder dokumentiert
- [ ] aktives SEO-Plugin dokumentiert
- [ ] Plugin-Inventar dokumentiert
- [ ] Backup bestaetigt
- [ ] Restore bestaetigt
- [ ] Rollback Owner benannt
- [ ] Validation Owner benannt

Evidence:

Outcome:

## Stage 1: Install

Status: `[ ] GO` `[ ] NO-GO`

- [ ] exakt dieses staging-only Paket lokal bereitgestellt
- [ ] Paket nur auf der staging-domain hochgeladen
- [ ] Plugin erscheint im WordPress-Admin als installiert
- [ ] Version `0.1.0-real-staging1` sichtbar
- [ ] keine Scope-Ausweitung vorgenommen

Evidence:

Outcome:

## Stage 2: Aktivierung

Status: `[ ] GO` `[ ] NO-GO`

- [ ] Plugin aktiviert ohne Fatal Error
- [ ] Startmodus ist `safe_mode` oder `observe_only`
- [ ] keine aktive Ownership-Uebernahme erlaubt
- [ ] kein anderes SEO-Plugin deaktiviert

Evidence:

Outcome:

## Stage 3: Sichtbare Verifikation

Status: `[ ] GO` `[ ] NO-GO`

- [ ] `/wordpress/` laedt ohne sichtbaren Schaden
- [ ] `/wordpress/beispiel-seite/` laedt ohne sichtbaren Schaden
- [ ] Head-Diagnostics sichtbar und plausibel
- [ ] Meta-Diagnostics sichtbar und plausibel
- [ ] Structure-Diagnostics sichtbar und plausibel
- [ ] Visibility-Diagnostics sichtbar und plausibel

Evidence:

Outcome:

## Stage 4: Coexistence Pass

Status: `[ ] GO` `[ ] NO-GO`

- [ ] Ownership der Head-Ausgabe ist klar
- [ ] Ownership der Meta-Ausgabe ist klar
- [ ] Theme-Konflikte sind dokumentiert oder ausgeschlossen
- [ ] Builder-Konflikte sind dokumentiert oder ausgeschlossen
- [ ] SEO-Plugin-Konflikte sind dokumentiert oder ausgeschlossen
- [ ] keine doppelte Head- oder Meta-Ausgabe sichtbar
- [ ] keine Scope-Verletzung ausserhalb `/wordpress/` und `/wordpress/beispiel-seite/`

Evidence:

Outcome:

## Stage 5: Rollback Drill

Status: `[ ] GO` `[ ] NO-GO`

- [ ] Plugin deaktivierbar
- [ ] wenn noetig Plugin entfernbar
- [ ] Rueckkehr in den Vorher-Zustand praktisch bestaetigt
- [ ] `/wordpress/` nach Rueckbau ok
- [ ] `/wordpress/beispiel-seite/` nach Rueckbau ok
- [ ] keine doppelte Meta-/Head-Ausgabe bleibt nach Rueckbau
- [ ] Rollback-Protokoll durch Rollback Owner dokumentiert

Evidence:

Outcome:

## Stage 6: Erste Kontrollierte Optimierungsstufe

Status: `[ ] GO` `[ ] NO-GO`

- [ ] nur Homepage-Meta-Readiness oder Diagnostics-Readiness freigegeben
- [ ] keine globale Site-Uebernahme
- [ ] keine Rank-Math-Ablosung
- [ ] reversible Vorbereitung bleibt eng und nachvollziehbar

Evidence:

Outcome:

## Finales Go / No-Go

Status: `[ ] GO TO REFERENCE PILOT` `[ ] STAY IN STAGING` `[ ] ROLLBACK AND REDESIGN`

- [ ] URL-Normalisierung bestanden
- [ ] Install bestanden
- [ ] Aktivierung bestanden
- [ ] sichtbare Verifikation bestanden
- [ ] Coexistence bestanden
- [ ] Rollback Drill bestanden
- [ ] Scope blieb eng
- [ ] keine Seitenschaeden
- [ ] keine Ownership-Unklarheit
- [ ] keine ungeklaerten Konflikte

Final Evidence:

Final Decision:

Final Decision Owner:

Final Decision Timestamp:

## Sofortiges No-Go

Wenn eines davon auftritt, ist die Entscheidung sofort `NO-GO`:

- fatal error
- sichtbare Seitenschaedigung
- doppelte Meta- oder Head-Ausgabe
- unklare Ownership
- domain mismatch
- rollback path broken
- Scope-Austritt

## 10/10-Regel

Eine ehrliche 10/10-Aussage ist erst zulaessig, wenn alle Blocking-Stufen dieses Dokuments auf `GO` stehen und die Commercial-, Signing-, Fulfillment- und Payment-Kette ebenfalls mit echter externer Evidence gruen ist.
