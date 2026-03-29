# Approval Gate Spec

## Zweck

Das approval_gate trennt Beobachtung, Blueprint, Freigabepflicht, Pilotbereitschaft und Rollback-Pflicht.

## Gate-Zustaende

- `observe_only`
- `data_insufficient`
- `blueprint_ready`
- `approval_required`
- `pilot_ready`
- `blocked`
- `rollback_required`

## Bedeutung der Zustaende

### observe_only

- nur Analyse, keine externe Aenderung

### data_insufficient

- Datenlage reicht nicht fuer belastbare Planung oder Validierung

### blueprint_ready

- Massnahme ist fachlich beschrieben, aber noch nicht freigegeben

### approval_required

- Freigabe, Zugangsdaten oder explizite Verantwortungsuebernahme fehlen

### pilot_ready

- Inputs, Freigaben, Validierungs- und Rollback-Schema sind vollstaendig

### blocked

- Massnahme ist zu riskant, zu unklar oder ausserhalb der erlaubten Grenzen

### rollback_required

- spaetere Pilot- oder Anwendungsmassnahme zeigt unakzeptable Nebenwirkungen

## Freigabepflicht

Freigabepflicht gilt spaeter immer fuer:

- Cloudflare-Schreiboperationen
- WordPress-, Theme- oder Plugin-Aenderungen
- Aktivierung von Scheduler-, Connector- oder Notification-Komponenten
- Aenderungen mit mittlerem oder hohem Blast Radius

## blocked / pilot_ready / approval_required / rollback_required

### blocked

Wird gesetzt bei:

- fehlendem Rollback
- unklarem Zielsystem
- unklarer Kausalitaet
- zu grossem Blast Radius
- Verstoessen gegen Sicherheitsgrenzen

### approval_required

Wird gesetzt bei:

- fehlenden Zugangsdaten
- fehlender Connector-Freigabe
- fehlender Betreiberzustimmung
- unvollstaendigen Zielbereichsdefinitionen

### pilot_ready

Wird gesetzt nur wenn:

- Blueprint vollstaendig
- Freigabe vorhanden
- Validierung definiert
- Rollback definiert
- Scope klein und kontrollierbar

### rollback_required

Wird spaeter gesetzt wenn:

- Primaermetrik sich nicht verbessert
- Nachbarsignale regressiv werden
- Status, Struktur oder Verfuegbarkeit kippen
- Personalisierung, Caching oder Markup fehlerhaft reagieren

## Entscheidungslogik pro Connector-Typ

### Observe-only

- Standardzustand: `observe_only`
- kann zu `blueprint_ready` wechseln, wenn Beobachtungen stabil und ausreichend sind
- darf nie zu externer Anwendung fuehren

### Cloudflare

- ohne freigegebene Zone und Regeltypen immer `approval_required`
- bei globalen oder schlecht begrenzten Regeln `blocked`
- nur mit klarer Pfadlogik und Rollback `pilot_ready`

### WordPress

- ohne Zielbereichsdefinition immer `approval_required`
- bei Core- oder siteweiten Risiken `blocked`
- nur mit engem Template-, Builder- oder Plugin-Scope `pilot_ready`

## Gate-Entscheidung als Pflichtobjekt

Jede spaetere Massnahme sollte mindestens speichern:

- connector_type
- target_scope
- risk_level
- blast_radius
- data_quality
- approval_status
- validation_ready
- rollback_ready
- final_gate_state
- gate_reason

