# Public Portal Information Architecture v2

## Zweck

Dieses Dokument ist die weiterentwickelte Informationsarchitektur fuer die Landingpage- und Unterseitenlogik des oeffentlichen Produktportals.

## IA v2

- Home
  Produktpositionierung, Referenzstatus, Differenzierung, FAQ, CTA
- Features
  Funktionslayer, Produktstack, Plugin-first-Argumentation
- Security
  Guardrails, Validation, Rollback, Route-Schutz
- Plugin
  Plugin-Ausfuehrungsmodell, Safe-Mode, Konfliktlogik, Rank-Math-Koexistenz
- Licensing
  Domain-Binding, Scope-Control, Release-Channels, offene kommerzielle Felder
- Docs
  Doku-Einstieg, Architekturpfad, Referenzbezug, aktuelle Grenzen
- Downloads
  gated Access, keine offene Package-Auslieferung
- Support
  Support-Einstieg, Klarstellung unbestaetigter Kontakt- und Commercial-Daten

## Navigationslogik

- primaere Navigation ist flach und klar
- Home bleibt die zentrale Hub-Seite
- Unterseiten verlinken gezielt in benachbarte Themen, nicht ungezielt sitewide

## Inhaltslogik

- jede Seite traegt einen klaren H1-Fokus
- jede Seite braucht eine sekundare Nutzrichtung ueber CTA und interne Links
- keine Seite soll geschuetzte Operator- oder Customer-Funktionen andeuten

## SEO-Logik

- Unterseiten erhalten eindeutige Titles und Descriptions
- Breadcrumbs nur auf Unterseiten
- FAQ-Markup nur dort, wo echte FAQ-Inhalte vorhanden sind

## Status

- IA v2: `blueprint_ready`
- spaetere Customer-Portal-Erweiterung: `approval_required`
