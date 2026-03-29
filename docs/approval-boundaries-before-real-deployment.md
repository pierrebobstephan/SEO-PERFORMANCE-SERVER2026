# Approval Boundaries Before Real Deployment

## Zweck

Dieses Dokument beschreibt die harten Freigabegrenzen vor jeder spaeteren realen Produktauslieferung.

## Freigabepflichtig bleiben

- jede echte License-Check-Verbindung
- jede echte Plugin-Download- oder Update-Auslieferung
- jede WordPress-Installation oder Aktivierung
- jede domaingebundene Policy-Verteilung
- jede Rollback-Profil-Verteilung an externe Zielsysteme
- jede aktive Meta-Description-Ausgabe
- jede aktive Rank-Math-Ersatzlogik

## Blockiert bis zur Klaerung

- unklare Domain-Bindung
- unklare Scope-Definition
- fehlendes Rollback-Profil
- fehlende Validation-Metriken
- unklare Theme-, Builder- oder SEO-Plugin-Konfliktlage
- fehlende Betreiberfreigabe

## Phasenbezogene Grenzziehung

- Phase 7 darf lokal validieren, aber keine reale Lizenz oder Kanalzuweisung ausrollen
- Phase 8 darf lokal Plugin-Code vorbereiten, aber keine Live-Installation oder aktive Homepage-Ausgabe ausfuehren
- Phase 9 darf lokale Vertragslogik modellieren, aber keine reale Control-Plane-Verbindung, Policy-Ausgabe oder Kundenanbindung herstellen

## Status

- Deployment-Grenzen: `blueprint_ready`
- reale Auslieferung: `approval_required`
