# Local Console Test Flow

## Zweck

Dieses Dokument beschreibt die lokal verfuegbaren Testaktionen der Browser-Konsole.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Alle Aktionen bleiben lokal und ohne Connector-Wirkung.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Die lokalen Testaktionen nicht.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Aktionen erzeugen nur lokale Prozessausgaben oder Preview-Daten.

## Lokale Testaktionen

- `Run Python Tests`
- `Validate Config`
- `Run Schema Checks`
- `Dry Run Onboarding`
- `Build Manifest Preview`
- `Build Package Metadata`
- `Build Release Artifact Preview`

## Zweck der Aktionen

- Python-Tests pruefen die lokale Python-Test-Suite
- Validate Config prueft den doctrine-enforced Workspace-Status
- Schema Checks pruefen Schemas und lokale Preview-Objekte
- Dry Run Onboarding prueft den lokalen Onboarding-Preview-Pfad
- Manifest / Package / Release bauen nur lokale Preview-Daten

## Status

- lokale Testaktionen: `blueprint_ready`
- echte Produktwirkung: `approval_required`
