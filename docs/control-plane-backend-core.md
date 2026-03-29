# Control Plane Backend Core

## Zweck

Dieses Dokument beschreibt den lokalen Backend-Core der Hetzner Control Plane fuer Lizenz-, Policy-, Manifest-, Rollback- und Onboarding-Objekte.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Der Backend-Core bleibt lokal, inert und validierungszentriert.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Jede spaetere reale Backend-Wirkung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Fehlende Preconditions stoppen auf `observe_only`, `blueprint_ready` oder `approval_required`.

## Lokale Artefakte

- `src/electri_city_ops/backend_core.py`
- `src/electri_city_ops/registry.py`
- `src/electri_city_ops/manifest_builder.py`
- `src/electri_city_ops/rollback_registry.py`
- `src/electri_city_ops/onboarding.py`
- `config/backend-defaults.json`

## Kernaufgaben

- Lizenzobjekte intern registrieren
- domaingebundene Policies intern registrieren
- Manifeste nur bei bestaetigten Preconditions vorbereiten
- Rollback-Profile domaingebunden verwalten
- Domain-Onboarding auf sichere Registry-Zustaende abbilden
- Backend-Zustand doctrine-konform ableiten

## Status

- Backend-Core: `blueprint_ready`
- reale Backend-Wirkung: `approval_required`
