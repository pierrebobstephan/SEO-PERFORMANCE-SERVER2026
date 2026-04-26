# Bridge Plugin Domain Binding Flow

## Ablauf

1. packaged bridge profile laden
2. current domain via `home_url('/')` erkennen
3. bound domain gegen `wp.electri-c-ity-studios-24-7.com` pruefen
4. allowed scopes laden
5. domain mismatch fuehrt auf `observe_only`
6. URL-Normalisierungsfehler fuehren auf `safe_mode`

## Gate

- Bridge Plugin Domain Binding Flow: `approval_required`
