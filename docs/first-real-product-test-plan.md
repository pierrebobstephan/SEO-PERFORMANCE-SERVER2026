# First Real Product Test Plan

## Ziel

Der erste echte Produkttest soll reproduzierbar und staging-orientiert sein.

## Testrahmen

- exakte licensed test domain
- Plugin in `safe_mode` oder `observe_only`
- nur ein klarer Scope
- Vorher-/Nachher-Vergleich

## Mindestablauf

1. Backup bestaetigen
2. Umgebung inventarisieren
3. Plugin installieren
4. in `safe_mode` aktivieren
5. erste Validierungschecks fahren
6. bei Problemen sofort abbrechen oder zurueckrollen

## Gate

- First Real Product Test Plan: `approval_required`
