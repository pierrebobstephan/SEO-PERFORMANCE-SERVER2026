# Plugin Rank Math Coexistence Model

## Zweck

Dieses Dokument beschreibt die kontrollierte Koexistenz zwischen dem eigenen Plugin-Pfad und Rank Math, solange Rank Math noch aktiv ist.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es verhindert unklare Doppelausgabe und abrupte Ablosung.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Jede spaetere lokale Aenderung auf der Ziel-Domain ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Rank Math bleibt bis spaet zurueckhaltende Ist-Quelle.

## Grundsaetze

- Rank Math bleibt aktuelle Ist-Situation
- keine abrupte Deaktivierung
- keine erzwungene Doppel-Ausgabe
- eigenes Plugin bleibt inaktiv, solange die Source-Ownership unklar ist

## Konfliktlogik

- ein aktives SEO-Plugin signalisiert mindestens `source_mapping_unclear`
- mehrere aktive SEO-Plugins sind `safe_mode`
- Rank Math plus unklare Homepage-Description-Quelle verhindern aktive Plugin-Ausgabe

## Migrationslogik

1. aktuelle Meta-/Title-/Canonical-/Robots-Quelle eindeutig mappen
2. nur Homepage-Description als erster Plugin-Scope vorbereiten
3. Doppel-Ausgabe technisch ausschliessen
4. Pilot validieren
5. erst danach weitere SEO-Funktionen schrittweise ersetzen
6. Rank Math erst am Ende kontrolliert deaktivieren

## Status

- Koexistenzmodell: `blueprint_ready`
- reale Ablosung: `approval_required`
