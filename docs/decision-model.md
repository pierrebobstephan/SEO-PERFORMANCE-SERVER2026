# Decision Model

## Ziel

Das Entscheidungsmodell soll spaeter sicherstellen, dass das System nicht aus Einzelbeobachtungen heraus handelt, sondern nur aus ausreichend stabilen, erklaerbaren und validierbaren Signalen.

## Wie Prioritaeten berechnet werden

Das aktuelle System nutzt bereits:

- Severity-Gewicht
- Risiko-Gewicht
- Confidence
- Wiederholungsbonus

Das langfristige Modell sollte daraus einen vollstaendigeren Prioritaetswert ableiten.

### Phase-3.5-Zielscore

`priority_score = impact + confidence + recurrence + feasibility + reversibility - uncertainty - blast_radius`

### Erklaerung der Komponenten

- `impact`: erwarteter Nutzen fuer SEO, Performance, Stabilitaet oder Ressourceneffizienz
- `confidence`: Verlaesslichkeit der Beobachtung und der Ursachenannahme
- `recurrence`: Wiederholung ueber mehrere Runs oder Zeitfenster
- `feasibility`: technische Umsetzbarkeit im Zielsystem
- `reversibility`: Qualitaet und Klarheit des Rollback-Pfads
- `uncertainty`: Datenluecken, Messrauschen, unklare Kausalitaet
- `blast_radius`: moeglicher Seiteneffekt auf andere Bereiche oder auf produktive Nutzer

## Wann etwas nur beobachtet wird

Eine Massnahme bleibt im Status `observe_only`, wenn mindestens einer der folgenden Punkte zutrifft:

- zu wenige Datenpunkte
- widerspruechliche Signale
- unklare Ursache
- keine sichere Zielsystem-Zuordnung
- keine Ruecknahmebeschreibung
- keine Freigabe fuer den spaeteren Connector
- Risiko fuer produktive Seiteneffekte ist hoeher als der erwartete Nutzen

## Wann etwas als Quick Win gilt

Eine Massnahme gilt als Quick Win, wenn alle Bedingungen erfuellt sind:

- Wirkung ist klar und zeitnah messbar
- technische Umsetzung ist klein und lokal begrenzt
- Rollback ist trivial oder sehr klar
- betroffene Flaeche ist eng begrenzt
- es gibt kein Signal fuer Nutzer- oder Inhaltsrisiko
- Vorher/Nachher-Messung kann ohne grossen Interpretationsspielraum erfolgen

Beispiele aus dem aktuellen Stand:

- Cloudflare-Kompression fuer HTML
- kontrollierte Cache-Regel fuer anonyme Homepage-Aufrufe
- H1-Konsolidierung
- Meta-Description-Nachschaerfung

## Wann eine Massnahme zu riskant ist

Eine Massnahme wird als `too_risky` oder `blocked` eingestuft, wenn einer der folgenden Punkte zutrifft:

- der Blast Radius ist gross und nicht sauber begrenzt
- das Zielsystem ist nicht klar freigegeben
- die Ruecknahme ist unklar
- Erfolg ist nicht in einem festen Fenster messbar
- es besteht Gefahr fuer personalisierte Inhalte, Session-Logik oder kritische Caches
- der Eingriff beruehrt WordPress-Core, globale Edge-Regeln oder systemweite Infrastruktur ohne enge Scope-Begrenzung

## Wann eine Freigabe erforderlich ist

Freigabe ist spaeter verpflichtend fuer:

- jede Cloudflare-Schreiboperation
- jede WordPress-, Theme- oder Plugin-Aenderung
- jede Aktivierung von Scheduler-, Notification- oder Connector-Komponenten
- jede Aenderung mit mittlerem oder hohem Blast Radius
- jede Massnahme, die nicht klar nur beobachtend oder rein lokal im Workspace bleibt

Keine Freigabe braucht:

- reine Analyse
- lokale Report-Erzeugung
- historische Auswertung
- Blueprint-Erzeugung ohne externe Anwendung

## Wie spaeter A/B-artige oder schrittweise Validierung aussehen soll

Das Ziel ist keine klassische Marketing-A/B-Test-Engine, sondern eine vorsichtige, technische Pilotvalidierung.

### Stufe 1: Baseline sichern

- vor jeder Aenderung ausreichend Historie sammeln
- relevante Kennzahlen und Referenzzeitfenster fixieren

### Stufe 2: Pilot-Scope klein halten

- zuerst nur eine einzelne Regel, ein einzelner Pfad oder ein eng begrenztes Template aendern
- keine kombinierten Grossmassnahmen ohne Einzelvalidierung

### Stufe 3: Validierungsfenster definieren

- Sofortfenster fuer technische Smoke-Checks
- Kurzfenster fuer 1d- und 7d-Vergleich
- spaeter Langfenster fuer 30d-Wirkung, falls noetig

### Stufe 4: Erfolg mehrdimensional bewerten

- positive Primaermetrik allein reicht nicht
- Nachbarsignale duerfen sich nicht klar verschlechtern
- Beispiel: bessere Cache-Werte duerfen nicht zu falscher Personalisierung oder regressiven HTML-Signalen fuehren

### Stufe 5: Stop- und Rollback-Regeln

- jede Pilotmassnahme hat vordefinierte Abbruchkriterien
- bei kritischen Seiteneffekten sofort rollback_required
- learning_engine speichert den Ausgang fuer spaetere aehnliche Entscheidungen

## Empfohlenes Zustandsmodell fuer spaetere Entscheidungen

- `observe_only`
- `data_insufficient`
- `blueprint_ready`
- `approval_required`
- `pilot_ready`
- `applied_pilot`
- `validated_success`
- `validated_mixed`
- `rollback_required`
- `blocked`

## Ableitung fuer den aktuellen Stand

Aus der aktuellen Analyse lassen sich heute bereits blueprint-faehig klassifizieren:

- Kompressionsthema
- Cache-Control-Thema
- H1-Konsolidierung
- Meta-Description-Optimierung
- HTML-Gewichtsreduktion

Sie bleiben trotzdem bis Phase 4 und bis zu expliziten Freigaben ohne Anwendung.

