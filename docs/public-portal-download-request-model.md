# Public Portal Download Request Model

## Zweck

Dieses Dokument beschreibt den oeffentlichen Vorbereitungszustand fuer spaetere Access Requests rund um Plugin-Downloads.

## Grundsatz

- Downloads bleiben gegated
- Access Requests werden inhaltlich vorbereitet, aber nicht live abgewickelt
- protected delivery bleibt getrennt von oeffentlicher Portal-Copy

## Oeffentliche Aussagen

- welche Informationen fuer spaetere Access Requests relevant sind
- warum protected delivery notwendig bleibt
- welche Kanaele spaeter domaingebunden gedacht sind
- welche Punkte weiterhin `approval_required` bleiben

## Nicht erlaubt

- direkter Download-Link
- offene `/downloads/private` Nutzung
- Login oder Customer-Portal
- offene Lizenz- oder Release-API

## Minimal benoetigte spaetere Inputs

- Ziel-Domain
- WordPress-Stack
- gewuenschter Scope
- Rollback-Owner
- Validation-Owner

## Status

- Download-Request-Modell: `blueprint_ready`
- echte Access-Request-Abwicklung oder Fulfillment: `approval_required`
