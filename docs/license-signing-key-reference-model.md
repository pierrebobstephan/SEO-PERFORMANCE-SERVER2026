# License Signing Key Reference Model

## Zweck

Dieses Dokument beschreibt, wie ein spaeterer Signing-Key nur referenziert, aber nicht im Repo gespeichert wird.

## Regeln

- kein Klartext-Key im Workspace
- nur `signing_key_reference`
- Referenz bleibt `operator_input_required`, bis ein realer Schluesselpfad freigegeben ist
- Test- und Produktionsschluessel duerfen nicht verwechselt werden

## Status

- Key-Reference-Modell: `blueprint_ready`
- reale Schluesselnutzung: `approval_required`
