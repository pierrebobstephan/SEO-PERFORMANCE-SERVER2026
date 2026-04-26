# Domain-Bound Pilot Package Model

## Ziel

Ein Pilotpaket soll spaeter nur fuer genau definierte Testdomains und Scopes gelten.

## Modell

- exakte licensed test domain
- explizite allowed scopes
- `pilot` release channel
- Rollback-Profil pro Domain
- keine Rechte ausserhalb des gebundenen Testscopes

## Preview-Artefakte

- package metadata preview
- domain-binding preview
- pilot manifest preview
- release artifact preview

## Gate

- Domain-Bound Pilot Package: `approval_required`
