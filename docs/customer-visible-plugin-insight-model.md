# Customer Visible Plugin Insight Model

## Ziel

- jedes installierte Bridge-Plugin zeigt gut lesbare, lokale Suite-Informationen
- keine Customer-API, kein Login, keine externe Delivery

## Sichtbare Bereiche

- Status Overview
- Subscription And Scope
- What The Installed Plugin Sees
- Baseline Evidence
- Safe Now
- What Stays Protected
- Next Steps Before Production
- License / Domain / Scope Panel
- Customer Subscription Visibility
- Installation Health Signals
- Protected Delivery Status
- Production Cutover Checklist

## 8.0-Doktrin in der Sichtflaeche

- die installierte Bridge soll nicht wie eine Black Box wirken
- der Kaeufer soll erkennen koennen:
  - warum etwas grün ist
  - warum etwas blockiert bleibt
  - was der naechste kleinste sichere Schritt waere
- buyer-readable Visibility ist Teil des Produkts, nicht nur Nebeneffekt der Admin-Oberflaeche

## Datenquellen

- Domain Binding und Lizenz-Snapshot
- Baseline-Snapshot
- Conflict-Snapshot
- Operator-Input-State
- Source-Mapping-State
- Optimization Gate

## Grenzen

- nur Admin-intern
- nur staging-only oder spaeter lizenziert lokal
- keine Oeffnung geschuetzter Routen
