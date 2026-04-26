# Global Usage Rights And Valuation Model

## Zweck

Dieses Modell beschreibt, wie globale Nutzungsrechte neutral bewertet werden, ohne Produktreife, Rechtslage oder externe Freigaben vorzutaeuschen.

## Aktuelle Rechteposition

- Repository-Zugriff gewaehrt keine globalen Nutzungsrechte.
- Staging-Pakete gewaehrleisten keine Kundenauslieferung.
- Public-Portal-Preise gewaehrleisten keine offenen Reseller-, White-Label- oder Multi-Domain-Rechte.
- Globale Nutzungsrechte brauchen einen separaten Vertrag und passende Production-Gates.
- WordPress-Plugin-Distribution muss vor oeffentlicher WordPress.org-Auslieferung GPL-kompatibel sein.

## Bewertungsachsen

Die Gesamtbewertung wird auf 10 Punkte normalisiert:

- Funktionalitaet und Testabdeckung: 2 Punkte
- Security und Secret-Hygiene: 2 Punkte
- Produkt-/Commercial-Chain: 2 Punkte
- Rechte-, Lizenz- und Compliance-Klarheit: 2 Punkte
- Referenzpilot, Betrieb und externe Validierung: 2 Punkte

## 10/10-Gates

Eine neutrale 10/10-Bewertung ist erst zulaessig, wenn alle Punkte belegt sind:

- alle lokalen Tests gruen
- PHP-Syntax- und WordPress-Runtime-Validation gruen
- keine Klartext-Secrets im Workspace
- alle vormals offengelegten Secrets rotiert
- PayPal-Webhooks real verifiziert und aktiviert
- geschuetzte Delivery real validiert
- Signing-Key- oder Signing-Service-Kette produktionsreif
- Referenzpilot bestanden
- Rollback-Drill bestanden
- Support-, Incident- und Billing-Verantwortung verbindlich
- globaler Nutzungsrechtevertrag geprueft und unterschrieben

## Neutraler Preisrahmen

Solange externe Gates offen sind, ist der realistische Rechtewert defensiv zu bewerten:

- Nicht-exklusive interne globale Nutzung: EUR 10k-40k einmalig oder EUR 1k-4k pro Monat
- Nicht-exklusive kommerzielle Nutzung mit Kundenauslieferung: EUR 50k-150k plus Support- oder Revenue-Share
- Exklusive globale Rechte inklusive Source-/IP-Transfer: EUR 120k-350k im aktuellen Vor-Go-Live-Zustand

Nach bestandenen 10/10-Gates kann der Rahmen neu bewertet werden. Eine plausible Zielspanne fuer exklusive globale Rechte kann dann hoeher liegen, muss aber durch Umsatz, Kundenbetrieb, Supportkosten, Haftung und rechtliche Struktur belegt werden.

## Status

- Rights Model: `implemented_locally`
- Current Neutral Rating Target: `10/10_only_after_external_gates`
- Current Production Claim: `not_allowed`
