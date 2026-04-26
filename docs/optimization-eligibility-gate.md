# Optimization Eligibility Gate

## Muss gruen sein

- domain match
- URL-Normalisierung sauber
- keine blocking conflicts
- scope confirmed
- source mapping confirmed
- rollback intakt

## Gelb

- source mapping unklar
- Rank Math aktiv aber Koexistenz noch unbestaetigt
- Rank Math aktiv, Koexistenz bestaetigt, Bridge bleibt aber auf `recommend_only`

## Rot

- Fatal Error
- sichtbare Seitenschaedigung
- domain mismatch
- URL-Reste auf `localhost`
- mehrere SEO-Plugins mit Konflikt

## Gate

- Optimization Eligibility Gate: `approval_required`
- `reversible_change_ready` nur ohne externen SEO-Owner in der Live-Ausgabe
