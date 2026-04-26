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
- bestaetigte Single-Source-Ownership unter Rank Math hebt den Zustand auf `recommend_only`, nicht auf sofortige Live-Uebernahme
- reversible oder aktive Live-Ausgabe bleibt gesperrt, solange ein externer SEO-Owner die Ausgabe kontrolliert

## Konfliktlogik

- mehrere aktive SEO-Plugins signalisieren `source_mapping_unclear`
- genau ein aktives SEO-Plugin kann als kontrollierter Koexistenzfall modelliert werden
- mehrere aktive SEO-Plugins sind `safe_mode`
- Rank Math plus unklare Homepage-Description-Quelle verhindern aktive Plugin-Ausgabe
- Rank Math plus bestaetigte Single-Source-Ownership erlauben bounded Diagnostics und `recommend_only`, aber keine Live-Uebernahme durch die Bridge

## Migrationslogik

1. aktuelle Meta-/Title-/Canonical-/Robots-Quelle eindeutig mappen
2. nur Homepage-Description als erster Plugin-Scope vorbereiten
3. Doppel-Ausgabe technisch ausschliessen
4. Pilot validieren
5. erst danach weitere SEO-Funktionen schrittweise ersetzen
6. Rank Math erst am Ende kontrolliert deaktivieren

## Status

- Koexistenzmodell: `blueprint_ready`
- kontrollierte Koexistenz: `recommend_only` nach gruenen Ownership-Signalen
- reale Ablosung: `approval_required`
