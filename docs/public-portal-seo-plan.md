# Public Portal SEO Plan

## Zweck

Dieses Dokument beschreibt die SEO-Basis fuer die oeffentliche Produkt-Subdomain.

## Primare SEO-Ziele

- klare thematische Ausrichtung auf WordPress SEO und Performance Optimization
- saubere interne Linkstruktur zwischen Produkt-, Sicherheits-, Plugin-, Lizenz- und Supportseiten
- starke Seitentitel und Meta-Descriptions ohne Duplikation der Hauptdomain
- konsistente Canonicals auf die Produkt-Subdomain
- crawlbare, schlanke Portalstruktur mit `robots.txt` und `sitemap.xml`

## Title- und Description-Muster

- Home: Produktplattform und Nutzenversprechen
- Features: Funktionsueberblick
- Security: Validation, Guardrails, Rollback
- Plugin: WordPress-Plugin-Ausfuehrungsmodell
- Licensing: Domain-Binding und Scope-Control
- Docs: Architektur- und Doku-Einstieg
- Downloads: gated Access, kein offener Download
- Support: Kontakt- und Support-Einstieg

## Strukturierte Daten

- `Organization` fuer die Produktmarke
- `SoftwareApplication` fuer den Produktkontext
- `FAQPage` auf Seiten mit echtem FAQ-Block
- `BreadcrumbList` auf Unterseiten mit klarer Pfadstruktur

## Crawl- und Index-Regeln

- Public-Routen bleiben indexierbar
- Protected-Routen bleiben via Reverse Proxy gesperrt und via `robots.txt` unattraktiv
- `sitemap.xml` listet nur oeffentliche Routen und `healthz`

## Interne Linkstrategie

- jede Seite verlinkt auf mindestens zwei fachlich benachbarte Seiten
- Home verteilt in Features, Security, Licensing, Plugin und Docs
- Downloads und Support verweisen auf Licensing und Security statt auf offene Aktionen

## Nicht-Ziele

- keine Customer- oder Operator-Endpunkte indexieren
- keine generischen SEO-Claims ohne Produktbezug
- keine Wiederverwertung von Hauptdomain-Texten

## Status

- SEO-Plan: `blueprint_ready`
- spaetere SEO-Expansion mit echter Search-Console- oder Analytics-Kopplung: `approval_required`
