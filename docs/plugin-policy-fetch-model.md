# Plugin Policy Fetch Model

## Zweck

Dieses Dokument beschreibt das spaetere domaingebundene Policy-Objekt fuer das Plugin.

## Prueffragen

1. Ist es doktrinkonform?
   Ja. Policies bleiben domain- und scopegebunden.
2. Bleibt es innerhalb des Workspace?
   Ja.
3. Hat es irgendeine externe Wirkung?
   Nein.
4. Braucht es Approval?
   Das Modell nicht. Jede spaetere Policy-Auslieferung ja.
5. Ist ein Rollback oder Rueckweg beschrieben?
   Ja. Fehlende oder widerspruechliche Policy fuehrt nicht zu aktiver Wirkung.

## Kernfelder

- `license_id`
- `bound_domain`
- `release_channel`
- `policy_version`
- `default_mode`
- `allowed_scopes`
- `module_flags`
- `rollback_profile_id`
- `issued_at`

## Sicherheitsregeln

- Policy-Domain muss zur Lizenz-Domain passen
- Policy-Scopes duerfen Lizenz-Scopes nicht erweitern
- fehlende Policy fuehrt auf `observe_only`
- ungueltige Policy fuehrt auf `safe_mode`

## Status

- Policy-Modell: `blueprint_ready`
- echte Policy-Verteilung: `approval_required`
