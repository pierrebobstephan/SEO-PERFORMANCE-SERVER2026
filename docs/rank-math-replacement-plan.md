# Rank Math Replacement Plan

## Zweck

Dieses Dokument beschreibt den doctrine-konformen Ablosungspfad fuer Rank Math im Kontext des primaeren WordPress-Plugin-Ausfuehrungspfads.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es beschreibt nur einen spaeteren, kontrollierten Migrationspfad.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede spaetere WordPress-Umsetzung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Rank Math bleibt bis zum Ende aktiv und wird erst zuletzt kontrolliert deaktiviert.

## Warum Rank Math derzeit noch nicht entfernt werden sollte

- Rank Math ist aktuell aktiv und damit Teil der realen SEO-Ausgabe
- die genaue aktuelle Quelle fuer Homepage Meta, Title, Canonical und Robots ist noch nicht eindeutig gemappt
- eine abrupte Entfernung koennte Snippet-, Canonical- oder Robots-Signale unbeabsichtigt veraendern
- der eigene Plugin-Pfad ist noch nicht validiert und darf Rank Math deshalb nicht unkontrolliert ersetzen

## Welche SEO-Funktionen vor einer Ablosung zuerst abgedeckt werden muessen

- aktuelle Homepage Meta-Description-Logik
- aktuelle Homepage Title-Logik
- aktuelle Homepage Canonical-Logik
- aktuelle Homepage Robots-Logik
- kontrollierte Vermeidung doppelter SEO-Ausgabe

Hinweis:

- weitere Rank-Math-Funktionen ausserhalb dieses Homepage-Scope sind `source not yet confirmed` und duerfen vor Mapping nicht als ersetzt gelten

## Welche Konflikte spaeter vermieden werden muessen

- doppelte Meta Description
- doppelte oder widerspruechliche Title-Ausgabe
- doppelte oder widerspruechliche Canonical-Tags
- widerspruechliche Robots-Meta
- zwei gleichzeitige Quellen fuer dieselben Homepage-Signale
- unklare Mischlogik zwischen Rank Math und eigenem Plugin

## Empfohlene Migrationsreihenfolge

1. Quelle der aktuellen Meta-/Title-/Canonical-/Robots-Logik eindeutig mappen
2. eigenen Plugin-Pfad fuer Homepage Description vorbereiten
3. Doppel-Ausgabe vermeiden
4. Pilot validieren
5. erst danach schrittweise Rank-Math-Funktionen ersetzen
6. Rank Math erst am Ende kontrolliert deaktivieren

## Doctrinische Leitplanken fuer die Migration

- kleiner, klarer Homepage-Scope
- keine siteweite Freigabeformulierung
- keine Spekulation ueber Theme, Builder oder Rank-Math-Overrides
- `apply -> validate -> rollback`
- Rank Math nur als aktuelle Ist-Situation dokumentieren, nicht abrupt ersetzen

## Aktueller Status

- Rank Math bleibt aktiv: `ja`
- eigener Plugin-Pfad als Ersatz ist validiert: `nein`
- Plugin Pilot 1 ist freigegeben: `nein`
- daher bleibt jede echte Ablosung bis auf Weiteres `approval_required`
