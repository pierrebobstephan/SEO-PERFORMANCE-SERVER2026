# Reference Site Pilot vs Customer Rollout

## Zweck

Dieses Dokument trennt den spaeteren Rollout auf der Referenzinstanz von spaeteren Kunden-Domains.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es staerkt Domain-Isolation und begrenzt Blast Radius.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Rollout-Modell nicht. Jede spaetere Domain-Anwendung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Jede Domain behalt ihren eigenen Rueckweg.

## Referenzinstanz

- `electri-c-ity-studios-24-7.com`
- dient als frueher, enger Test- und Pilotpfad
- ersetzt nicht die Pflicht zur domaingebundenen Einzelpruefung

## Kunden-Domains

- eigene Lizenz pro Domain
- eigenes Scope-Set
- eigener Kanal
- eigenes Rollback-Profil
- eigene Konfliktbewertung

## Cross-Domain-Learning

- nur abstrahierte Muster
- keine riskante Mehrdomain-Verallgemeinerung
- keine automatische Massenanwendung

## Status

- Rollout-Trennung: `blueprint_ready`
- echte Kundenanbindung: `approval_required`
