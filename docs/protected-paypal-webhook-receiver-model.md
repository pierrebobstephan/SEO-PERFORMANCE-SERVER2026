# Protected PayPal Webhook Receiver Model

## Ziel

Der PayPal-Webhook-Empfaenger wird als geschuetzter, serverseitiger Billing-Receiver modelliert und bewusst von allen oeffentlichen Public-Portal-Seiten getrennt.

## Modellierter Receiver

- candidate protected receiver URL:
  - `https://site-optimizer.electri-c-ity-studios-24-7.com/protected/paypal/webhook`
- receiver state:
  - `modeled_protected_candidate`
- delivery scope:
  - `paypal_billing_events_only`
- verification model:
  - `server_side_signature_verification_with_env_ref_webhook_id`
- replay protection expectation:
  - `transmission_id_time_window_and_nonce_registry`

## Boundaries

- kein Public-Portal-Route-Ziel
- kein Customer-Login
- keine offene Billing-API
- keine Live-Aktivierung aus dem Workspace
- lokaler Self-Test fuer Signatur- und Replay-Pfad ist zulaessig, ersetzt aber keine reale Server-Verifikation
- weiter `approval_required`, bis Server-Receiver, Env-Refs und reale Verifikation geschlossen sind
