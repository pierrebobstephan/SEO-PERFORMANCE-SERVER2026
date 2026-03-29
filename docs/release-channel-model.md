# Release Channel Model

## Zweck

Dieses Dokument beschreibt das domaingebundene Kanalmodell `stable`, `pilot` und `rollback`.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Es bindet Freigaben und Rueckwege direkt an den Kanal.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Dokument nicht. Jede spaetere Kanalzuweisung pro Domain ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. `rollback` ist eigener Kanal.

## Kanaele

### stable

- nur fuer freigegebene, validierte und bewusste Domain-Zustaende
- keine experimentellen Features

### pilot

- nur fuer explizit freigegebene Domain-Piloten
- enger Scope
- staerkere Beobachtung
- schneller Rueckweg

### rollback

- definiert Rueckfall auf vorherige Plugin- und Policy-Version
- domaingebunden

## Kanalbindung

Jede Domain darf spaeter genau einem freigegebenen Hauptkanal zugeordnet sein.

Nicht erlaubt:

- gleichzeitige widerspruechliche Mehrkanal-Aktivierung
- globaler Kanalwechsel ueber mehrere Kunden-Domains ohne Einzelfreigabe

## Uebergaenge

- `stable -> pilot`: nur mit Domain-Freigabe
- `pilot -> stable`: nur nach Validierung
- `pilot -> rollback`: bei Regressions- oder Konfliktsignalen
- `stable -> rollback`: bei kritischer Regression

## Lokale technische Verankerung

- `config/release-channels.json`
- `src/electri_city_ops/product_core.py`
- `tests/test_product_core.py`

## Status

- Kanalmodell: `blueprint_ready`
- echte Kanalnutzung: `approval_required`
