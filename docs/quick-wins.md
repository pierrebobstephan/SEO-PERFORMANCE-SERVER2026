# Quick Wins

Diese Punkte sind als risikoarme Sofortmassnahmen priorisiert, werden hier aber nicht angewendet.

## 1. HTML-Kompression am Edge aktivieren

Umsetzungszone: `Cloudflare`

Warum jetzt:
Die Homepage liefert derzeit kein `Content-Encoding`, obwohl fast `184 KB` HTML uebertragen werden.

Erfolg waere messbar an:
Vorhandenem `Content-Encoding` im Report und stabiler oder besserer `response_ms`.

## 2. Homepage-Cache-Regel fuer anonyme Besucher pruefen

Umsetzungszone: `Cloudflare`

Warum jetzt:
`Cache-Control: no-cache` verschenkt vermutlich Edge-Potenzial auf der oeffentlichen Homepage.

Erfolg waere messbar an:
Kontrollierterem Cache-Header und keiner Verschlechterung der Response-Zeit in den Rollups.

## 3. Eine einzige primaere H1 auf der Homepage herstellen

Umsetzungszone: `WordPress/Themes/Plugins only`

Warum jetzt:
Der aktuelle Lauf zeigt `H1 count: 2`, was sich meist schnell und risikoarm im Template bereinigen laesst.

Erfolg waere messbar an:
`H1 count: 1` im naechsten validierten Lauf.

## 4. Meta Description auf vollwertige Snippet-Laenge erweitern

Umsetzungszone: `WordPress/Themes/Plugins only`

Warum jetzt:
Die aktuelle Description hat nur `40` Zeichen und nutzt den Snippet-Raum nicht aus.

Erfolg waere messbar an:
Meta-Description-Laenge im Bereich von etwa `140-160` Zeichen bei gleichbleibender Themenklarheit.

## 5. Nicht essenzielles Homepage-Markup abbauen

Umsetzungszone: `WordPress/Themes/Plugins only`

Warum jetzt:
`183759 bytes` HTML sind fuer eine Startseite ein realistischer Hebel mit relativ guter Sichtbarkeit im Monitoring.

Erfolg waere messbar an:
Sinkendem `html_bytes`-Trend ohne Layout- oder Inhaltsregression.

