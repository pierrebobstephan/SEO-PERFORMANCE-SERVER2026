# Rollback Playbooks

## Allgemeine Rollback-Regeln

- jede spaetere aendernde Massnahme braucht einen dokumentierten Vorzustand
- kein Pilot ohne definierte Ruecknahme
- Rollback muss denselben Scope treffen wie die Ausgangsaenderung
- Rollback muss messbar bestaetigt werden
- Rollback-Ergebnis wird spaeter historisiert

## Cloudflare-Rollback

### Ausloeser

- fehlerhafte Cache-Wirkung
- verschlechterte Statuscodes
- unerwartete HTML- oder Routing-Effekte
- schlechtere Primaermetrik ohne Nutzengewinn

### Rueckweg

- Regel deaktivieren oder auf dokumentierten Vorzustand zuruecksetzen
- Scope und Pfade unveraendert lassen
- keine zusaetzlichen Edge-Regeln gleichzeitig einfuehren

### Nachkontrolle

- Sofort-Messung fuer Header, Statuscode und Response-Zeit
- 1d-Follow-up fuer Stabilitaet

## WordPress-Rollback

### Ausloeser

- sichtbarer Layout-Bruch
- semantische Regression bei H1, Title oder Meta
- ungewolltes HTML-Wachstum
- fehlerhafte Plugin- oder Builder-Ausgabe

### Rueckweg

- Rueckkehr zum dokumentierten Vorzustand fuer Theme-, Builder- oder Plugin-Ebene
- kein Misch-Rollback ueber mehrere Zielbereiche
- zuerst die zuletzt eingefuehrte Massnahme ruecknehmen

### Nachkontrolle

- Sofort-Messung fuer HTML-Struktur und Kernfelder
- 1d- und optional 7d-Nachbeobachtung

## Beobachtungs- und Eskalationspfad

### Nach einem Rollback

- Status auf `rollback_required` oder spaeter `validated_mixed`
- Ursache dokumentieren
- Blast Radius bewerten
- learning_engine fuer spaetere aehnliche Blueprints informieren

### Eskalation

- bei wiederholtem Fehlschlag gleicher Change-Klasse auf `blocked`
- bei unklarer Kausalitaet zurueck in `observe_only`
- bei fehlender Ruecknehmbarkeit kein weiterer Pilot derselben Klasse

## Rollback als Pflichtbestandteil jedes Change-Blueprints

Jeder spaetere Blueprint muss beantworten:

- was genau wurde geaendert
- wie wird der Vorzustand wiederhergestellt
- wann wird zurueckgerollt
- welche Messung bestaetigt den erfolgreichen Rollback

