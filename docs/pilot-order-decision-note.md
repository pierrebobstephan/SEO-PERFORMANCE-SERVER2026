# Pilot Order Decision Note

## Ergebnis

Pilot Candidate 1 sollte zuerst vorbereitet und spaeter, nur nach Freigabe, vor Pilot Candidate 2 betrachtet werden.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es ist nur eine lokale Entscheidungsnotiz.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Die Notiz selbst nicht. Beide Piloten bleiben `approval_required`.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Es gibt keine Anwendung; die Reihenfolge kann spaeter neu bewertet werden.

## Warum Pilot 1 zuerst sinnvoller ist

- kleinere funktionale Aenderung
- geringerer inhaltlicher und technischer Blast Radius
- einfachere Validierung ueber `content_encoding`, Statuscode und Response-Verhalten
- geringeres Risiko fuer Personalisierung, Sessions oder Stale-Content
- klarerer Rueckweg

## Warum Pilot 2 danach kommen sollte

- Cache-Regeln haben hoehere Wechselwirkungen
- falsche Ausnahme-Logik kann personalisierte oder Preview-Inhalte verfaelschen
- es werden mehr Betreiberinputs fuer Ausschluesse und Bypass-Regeln benoetigt
- Kompression liefert vorher bereits ein sauberes, risikoaermeres Cloudflare-Lernsignal

## Aktueller Status

- Pilot 1: `approval_required`
- Pilot 2: `approval_required`
- ohne weitere Betreiberinputs und Freigaben bleibt keine Pilotanwendung zulaessig
