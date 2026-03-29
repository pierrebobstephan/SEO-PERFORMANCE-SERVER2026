# Operations

## Betriebsmodus

Der Stack bleibt standardmaessig in `observe_only`.

- keine externen Schreibzugriffe
- keine Aenderungen an Rocket Cloud
- keine Aenderungen ausserhalb `/opt/electri-city-ops`
- nur read-only HTTP-Pruefungen gegen freigegebene Ziele

## Standardablauf

1. Konfiguration validieren.
2. Einen Zyklus lokal ausfuehren.
3. `latest.json`, `latest.md` und die Rollups pruefen.
4. Findings und geplante Aktionen bewerten.
5. Vor jeder weitergehenden Eingriffstiefe explizite Freigabe einholen.

## Wichtige Kommandos

```bash
PYTHONPATH=src python3 -m electri_city_ops validate-config --config config/settings.toml
PYTHONPATH=src python3 -m electri_city_ops run-cycle --config config/settings.toml
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Report-Artefakte

- `var/reports/latest.json`
- `var/reports/latest.md`
- `var/reports/rollups/1d.json`
- `var/reports/rollups/7d.json`
- `var/reports/rollups/30d.json`
- `var/reports/rollups/365d.json`
- `var/state/ops.sqlite3`

## Trendinterpretation

- `response_ms`: sinkend ist besser, steigend ist schlechter
- `html_bytes`: sinkend ist besser, steigend ist schlechter
- `insufficient_data`: noch nicht genug historische Punkte
- `flat`: kaum veraendert

## Historische Lernhinweise

Wenn fruehere `observe_only`-Laeufe ohne Ziel-Domain existieren, markiert der Report diese explizit als systemweite Baseline. Diese Hinweise sind dann nicht als domain-spezifische Inhaltsbewertung zu lesen.

## Vorlagen

Unter `deploy/systemd/` und `deploy/cron/` liegen nur Vorschlaege.

- nichts wird automatisch installiert
- nichts wird aktiviert
- Anpassungen muessen vor Nutzung explizit freigegeben werden

