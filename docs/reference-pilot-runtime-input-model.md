# Reference Pilot Runtime Input Model

## Zweck

Der Referenzpilot darf nicht aus alten Preview- oder Pre-Install-Artefakten als "bestanden" erscheinen. Deshalb gibt es eine eigene Runtime-Evidenzdatei:

- `config/reference-pilot-runtime-input.json`

Sie repraesentiert den echten, lokal exportierten Zustand der installierten Bridge auf dem Referenzsystem.

## Rolle im Gate-Modell

Diese Datei ist keine Marketing-, Preview- oder Hand-off-Datei, sondern ein normalisiertes Gate-Input fuer:

- `src/electri_city_ops/productization.py`
- `manifests/previews/final-global-productization-readiness.json`

Wenn die Runtime-Evidenz fehlt, unvollstaendig ist oder die Validierung nicht besteht, bleibt der Referenzpilot defensiv:

- `status = operator_input_required`
- kein stillschweigender Uebergang auf `passed`
- kein automatisches Gruen fuer spaetere Produkt- oder Sales-Gates

## Quelle

Bevorzugte Exportquelle aus dem installierten Plugin:

- `runtime_context.reference_pilot_runtime_snapshot`

Fallback-Quellen, wenn der direkte Snapshot noch nicht isoliert vorliegt:

- `runtime_context`
- `validation_snapshot`
- `license_domain_scope_panel`
- `installation_health_signals`
- `operator_input_state`
- `source_mapping_state`

Die direkte Snapshot-Struktur hat Vorrang. Fallbacks dienen nur dazu, einen defensiv normalisierten Input zu erzeugen.

## Pflichtfelder

Im erfassten Runtime-Input muessen mindestens sauber vorliegen:

- `schema_version`
- `source`
- `status`
- `captured_at`
- `bound_domain`
- `current_domain`
- `path_base`
- `domain_match`
- `url_normalization_clean`
- `baseline_captured`
- `blocking_conflicts`
- `mode`
- `optimization_gate`
- `operator_inputs_complete`
- `source_mapping_confirmed`
- `open_blockers`
- `next_smallest_safe_step`
- `notes`

## Bedeutungen der Kernfelder

- `bound_domain`: exakt gebundene Referenzpilot-Domain
- `current_domain`: tatsaechlicher Host der installierten Bridge
- `path_base`: WordPress-Basis wie `/wordpress/`
- `domain_match`: nur `true`, wenn gebundene Domain und aktuelle Domain wirklich uebereinstimmen
- `url_normalization_clean`: nur `true`, wenn keine `localhost`- oder aehnlichen Restreferenzen mehr im relevanten Scope vorliegen
- `baseline_captured`: nur `true`, wenn der echte Before-State bereits aus der installierten Bridge erfasst wurde
- `blocking_conflicts`: `green` oder `blocked`
- `mode`: aktueller defensiver Plugin-Modus
- `optimization_gate`: `blocked`, `recommend_only` oder `reversible_change_ready`
- `operator_inputs_complete`: nur `true`, wenn die fuer den Pilot benoetigten Pflichtinputs wirklich erfasst sind
- `source_mapping_confirmed`: nur `true`, wenn Ownership und Single-Source-Signale real bestaetigt sind
- `open_blockers`: verbleibende harte Blocker, nicht nur Hinweise
- `next_smallest_safe_step`: naechste kleinste sichere Aktion, die direkt aus dem installierten Runtime-Stand folgt

## Builder

Lokaler Builder:

```bash
PYTHONPATH=src python3 tools/build_reference_pilot_runtime_input.py \
  --input path/to/installed-bridge-runtime-export.json \
  --output config/reference-pilot-runtime-input.json
```

Der Builder:

1. liest einen Runtime-Export der installierten Bridge
2. normalisiert die Struktur auf das Repo-Gate-Format
3. validiert das Ergebnis
4. schreibt die Datei nur, wenn der Input konsistent ist

Direkt anschliessender lokaler Closeout-Pfad:

- [reference-pilot-closeout-runbook.md](/opt/electri-city-ops/docs/reference-pilot-closeout-runbook.md)

Lokale Beispielquelle fuer den Builder:

- [reference-pilot-installed-bridge-runtime-export.json](/opt/electri-city-ops/manifests/previews/reference-pilot-installed-bridge-runtime-export.json)

Diese Datei ist bewusst nur eine lokale, strukturtreue Exportprobe. Sie ersetzt keinen echten Runtime-Export vom installierten Referenzpilot-System.

## Validierung

Die Validierung erfolgt in:

- `validate_reference_pilot_runtime_input(...)` in [productization.py](/opt/electri-city-ops/src/electri_city_ops/productization.py)
- `schemas/reference-pilot-runtime-input.schema.json`
- [test_reference_pilot_runtime_input.py](/opt/electri-city-ops/tests/test_reference_pilot_runtime_input.py)

Wichtige Validierungsregeln:

- `status` darf nur `operator_input_required` oder `captured_from_installed_bridge` sein
- `source` muss `installed_bridge_runtime_snapshot` sein
- `bound_domain` muss eine gueltige Domain sein
- `path_base` muss mit `/` beginnen und enden
- die Kern-Gates muessen echte Booleans sein
- `optimization_gate` darf nur bekannte Werte tragen

## Failure Model

Der Capture-Pfad ist bewusst fail-closed:

- ungueltige Runtime-Evidenz erzeugt keinen stillschweigenden Gruenstatus
- unvollstaendige Runtime-Evidenz wird nicht "erraten"
- invalides Input-Material wird als Blocker in die Produktisierungslogik zurueckgegeben

Das schliesst insbesondere diese Fehler aus:

- alter Hand-off-JSON-Stand wird als frischer Runtime-Stand interpretiert
- einzelne gruen wirkende Signale ueberschreiben offene Blocker
- Referenzpilot-Gruen wird aus Preview-Artefakten abgeleitet

## Minimaler Betriebsablauf

1. Installierte Bridge auf dem Referenzsystem liefert Runtime-Export.
2. Builder erzeugt `config/reference-pilot-runtime-input.json`.
3. Produktisierungslogik bewertet diesen Input.
4. Nur bei konsistenter Evidenz duerfen spaetere Referenzpilot-Gates weiterlaufen.

## Doktrin

Solange diese Runtime-Evidenz fehlt oder unklar ist, bleibt der Referenzpilot:

- `operator_input_required`

und darf nicht als bestanden, stabil oder verkaufsreif behandelt werden.
