# Public Portal Access Readiness Model

## Zweck

Dieses Dokument beschreibt die sichtbare Access- und Download-Readiness-Schicht des Portals.

## Sichtbare Signale

- `access_request_state`
- `legal_readiness_state`
- `download_readiness_state`
- `download_gate_state`

## Portalwirkung

- zeigt readiness und Gating
- zeigt keine echte Anfrageabwicklung
- zeigt keine Downloadfreigabe

## Grenzen

- keine Formulare
- keine Login-Ebene
- keine private Download-Route
- keine Lizenz- oder Entitlement-Ausgabe

## Verwendung im Portal

- `/buy`
- `/downloads`
- `/licensing`
- `/support`
- Readiness-Summary-Komponente

## Status

- Access-Readiness-Modell: `blueprint_ready`
- echte Access- oder Download-Abwicklung: `approval_required`
