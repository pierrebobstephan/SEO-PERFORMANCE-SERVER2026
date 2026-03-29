# Plugin Connector Priority Shift

## Ergebnis

Der primaere spaetere Connector-Pfad verschiebt sich von Cloudflare zu einem WordPress-Plugin auf IONOS WordPress. Dieser Plugin-Pfad ist zugleich als spaeter lizenzierbares Multi-Domain-Produktmodell zu lesen.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Nur die Priorisierung verschiebt sich, nicht die Schutzgrenzen.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Spaetere Plugin- oder Cloudflare-Anwendung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Ohne Freigabe bleibt alles observe-only oder approval_required.

## Vorher

- primaerer Pfad: `Cloudflare`
- sekundaerer Pfad: `WordPress`

## Jetzt

- primaerer Pfad: `WordPress plugin`
- sekundaerer Pfad: `Cloudflare`
- Produkt-Backend: `Hetzner control plane`

## Begruendung

- die wichtigsten aktuellen Hebel liegen in H1, Description, Markup und HTML-Gewicht
- diese Hebel sind im WordPress-Ausgabepfad naeher an ihrer Ursache
- Cloudflare adressiert spaeter eher Kompression, Header und Cache

## Folgen fuer die Dokumentlandschaft

- Plugin-Pilotdokumente werden vorrangig vorbereitet
- bestehende Cloudflare-Pilotdokumente bleiben erhalten, aber als sekundaere Pfade
- Priorisierungsdokumente lesen WordPress-Plugin nun als primaere Umsetzungszone
- Produkt-, Lizenz-, Domain-Binding-, Update- und Kundenmodell werden domaingebunden spezifiziert
