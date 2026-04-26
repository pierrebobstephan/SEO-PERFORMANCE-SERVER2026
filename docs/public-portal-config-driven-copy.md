# Public Portal Config Driven Copy

## Zweck

Dieses Dokument beschreibt, wie Portalcopy und Platzhalter aus Konfiguration statt aus fest verdrahteter Copy gespeist werden.

## Prinzip

- feste Produkt- und Sicherheitslogik bleibt im Code
- spaeter befuellbare Betreiberfelder kommen aus `config/public-portal-operator.json`
- unbefuellte Felder bleiben sichtbar ehrlich
- Buy-, Licensing-, Support- und Download-Readiness duerfen config-getrieben sichtbarer werden, ohne Protected Routes zu oeffnen

## Vorteile

- bessere Pflege spaeterer Live-Texte ohne Route- oder Schutzlogik zu aendern
- keine falsche Vollstaendigkeit bei noch offenen Kontakt- oder Commercial-Daten
- readiness summaries koennen sichtbar verbessert werden, ohne protected execution zu oeffnen
- Audience- und Buy-Seiten koennen denselben sichtbaren Statuskontext konsistent wiederverwenden

## Status

- config-driven copy: `blueprint_ready`
