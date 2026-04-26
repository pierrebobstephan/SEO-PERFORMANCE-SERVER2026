# Local Failed Payment Recovery Model

## Zweck

Dieses Dokument beschreibt die lokale, geschuetzte Vorbereitung fuer spaetere Failed-Payment-Recovery.

## Regeln

- keine automatische Sperrung oder Site-Wirkung
- `hold_future_delivery_only` statt direkter Eingriff
- Grace- und Retry-Logik bleiben ausserhalb des Workspace
