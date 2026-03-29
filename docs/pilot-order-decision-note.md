# Pilot Order Decision Note

## Ergebnis

WordPress-Plugin-Piloten sind ab jetzt der primaere spaetere Umsetzungspfad. Die bisherigen Cloudflare-Piloten bleiben erhalten, aber nur als sekundaere Folgepfade.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es ist nur eine lokale Entscheidungsnotiz.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Die Notiz selbst nicht. Plugin- und Cloudflare-Piloten bleiben bis zu weiteren Inputs `approval_required`.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Es gibt keine Anwendung; die Reihenfolge kann spaeter neu bewertet werden.

## Primaere Reihenfolge jetzt

1. [plugin-pilot-candidate-1.md](/opt/electri-city-ops/docs/plugin-pilot-candidate-1.md)
2. weitere WordPress-Plugin-Piloten fuer H1, Struktur und HTML-/Markup-Reduktion
3. erst danach die bisherigen Cloudflare-Pfade

## Warum der Plugin-Pfad zuerst sinnvoller ist

- die priorisierten Befunde liegen vor allem in Snippet-, H1-, Struktur- und Markup-Themen
- diese Themen entstehen primaer im WordPress-Ausgabepfad, nicht am Edge
- Plugin-seitige Aenderungen sind semantisch naeher an Ursache und Ziel
- Cloudflare-Cache- und Edge-Themen haben hoehere Risiken fuer Personalisierung und Stale-Content

## Reihenfolge innerhalb der Cloudflare-Sekundaerpfade

- zuerst der bisherige Kompressionspfad
- danach erst Cache-Regeln fuer anonyme Homepage-Requests
- Grund: Kompression hat den kleineren funktionalen Blast Radius als Caching

## Aktueller Status

- Plugin Pilot 1: `approval_required`
- Cloudflare Pilot 1: `approval_required`
- Cloudflare Pilot 2: `approval_required`
- ohne weitere Betreiberinputs und Freigaben bleibt keine Pilotanwendung zulaessig
