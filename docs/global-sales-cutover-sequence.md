# Global Sales Cutover Sequence

## Zweck

Dieses Dokument beschreibt die Reihenfolge, in der der lokale Produktstand spaeter in einen globalen Verkaufsstand uebergehen darf.

## Reihenfolge

1. lokale Checkout-to-Issuance-Orchestrierung ist konsistent
2. lokale Payment-Confirmation, Invoice-Confirmation und Customer-Release-Decision sind konsistent
3. lokale Renewal- und Failed-Payment-Recovery-Vorstufen sind konsistent
4. reale Checkout- und Invoice-Systeme sind freigegeben
5. reale Signing- und Replay-Schutz-Kette ist freigegeben
6. geschuetzte Customer-Delivery ist freigegeben
7. Referenzpilot und Rollback-Evidenz sind bestanden
8. globale Sales Go Live Gates sind gruen

## Status

- Sequenz: `blueprint_ready`
- globaler Verkaufsstand: `approval_required`
