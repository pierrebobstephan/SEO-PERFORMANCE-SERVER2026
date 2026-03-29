# Local Plugin Safe Mode Spec

## Zweck

Dieses Dokument beschreibt den lokalen Safe-Mode des spaeteren WordPress-Plugins.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Safe-Mode ist die direkte lokale Umsetzung des defensiven Defaults.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Safe-Mode als spaetere Plugin-Reaktion nicht separat, aber jede vorgelagerte echte Aktivierung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Safe-Mode selbst ist bereits ein Rueckzugszustand.

## Safe-Mode als Default

Safe-Mode greift spaeter standardmaessig, wenn:

- Lizenz unklar ist
- Domain-Binding unklar ist
- Scope unklar ist
- Konfliktlage unklar ist
- Policy fehlt oder inkonsistent ist
- Rollback-Profil fehlt

## Verhalten im Safe-Mode

- keine aktive Optimierungswirkung
- nur lokale Diagnose und Statusmeldung
- keine Aenderung an Theme, Builder oder SEO-Ausgabe
- Rueckfall auf read-only oder minimalen Diagnosepfad

## Exit aus Safe-Mode

Nur wenn zugleich gilt:

- Lizenz gueltig
- Domain passt
- Scope ist klar
- Konfliktlage ist akzeptabel
- Rollback ist definiert
- Validierung ist definiert

## Lokale technische Verankerung

- `packages/wp-plugin/hetzner-seo-ops/includes/class-hso-safe-mode.php`
- `src/electri_city_ops/contracts.py`
- `docs/runtime-guardrails.md`

## Status

- Safe-Mode-Spezifikation: `blueprint_ready`
- echter Plugin-Safe-Mode-Betrieb: `approval_required`
