# Domain Scoped Rollback Distribution

## Zweck

Dieses Dokument beschreibt die spaetere domaingebundene Verteilung von Rollback-Profilen.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Rollback bleibt domain- und scopegebunden.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Spaetere Verteilung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Das Dokument selbst beschreibt ihn.

## Rollback-Profil

- `rollback_profile_id`
- `bound_domain`
- `release_channel`
- `rollback_channel`
- `rollback_steps`
- `verification_checks`
- `abort_triggers`
- `issued_at`

## Verteilungsregeln

- genau einer gebundenen Domain zugeordnet
- darf nur die Scopes betreffen, die fuer die Domain freigegeben sind
- ohne passendes Rollback-Profil kein `active_scoped`

## Status

- Rollback-Distributionsmodell: `blueprint_ready`
- echte Verteilung: `approval_required`
