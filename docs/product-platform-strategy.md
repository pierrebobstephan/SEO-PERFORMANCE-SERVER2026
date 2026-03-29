# Product Platform Strategy

## Zweck

Dieses Dokument erweitert die bisherige Einzelprojekt-Sicht auf ein lizenzierbares Multi-Domain-WordPress-Produktmodell.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es beschreibt nur Produktarchitektur, keine aktive Fremdwirkung.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede spaetere Domain-Anbindung, Plugin-Auslieferung oder Aenderung pro Kunden-Domain ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ohne Lizenzaktivierung und Freigabe bleibt jede Domain in `observe_only`, `blueprint_ready` oder `approval_required`.

## Zielbild

Das System entwickelt sich von einer referenzsystem-zentrierten Optimierungsinstanz zu einem lizenzierbaren WordPress-Produkt mit zwei Ebenen:

- Hetzner-Server als doctrine-enforced Produkt-Backend / Control Plane
- WordPress-Plugin als lokale Ausfuehrung auf der jeweils lizenzierten Domain

## Rollenmodell

### Hetzner Control Plane

- verwaltet Lizenzen, Domain-Bindings, Policies, Update-Metadaten, Rollback-Plaene und Validierungslogik
- bleibt das Beobachtungs-, Lern-, Planungs- und Reporting-System
- fuehrt keine ungedeckten globalen Aenderungen ueber Kunden-Domains aus

### WordPress Plugin

- wird spaeter pro Domain lokal installiert
- setzt nur domain-, lizenz- und scopegebundene Optimierungen um
- meldet Status, Version und Validierungssignale an die Control Plane zurueck, soweit spaeter freigegeben

## Zielsysteme

### Referenzsystem

- `electri-c-ity-studios-24-7.com`
- dient als Referenz-, Lern- und Testinstanz
- ist nicht das einzige spaetere Zielsystem

### Kunden-Websites

- sind spaetere, getrennte Zielsysteme
- jede Website erhaelt einen eigenen Lizenz- und Scope-Kontext
- keine Website erbt automatisch Rechte oder Policies einer anderen Domain

## Produktprinzipien

- eine Lizenz bindet ein Plugin an genau definierte Domain-Grenzen
- Updates, Policies und Rollbacks werden je Domain versioniert
- Konflikte mit Theme, Builder und SEO-Plugins werden pro Domain einzeln bewertet
- der Hetzner-Stack bleibt auch im Produktmodell doctrine-enforced und defensiv

## Status

- Produktmodell: `blueprint_ready`
- Referenzsystem: `observe_only` fuer reale Wirkung
- Kunden-Websites: `blueprint_ready`
