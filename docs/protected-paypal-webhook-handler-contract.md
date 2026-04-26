# Protected PayPal Webhook Handler Contract

## Request

- method: `POST`
- path: `/protected/paypal/webhook`
- content type: JSON
- PayPal transmission headers werden erwartet

## Mindestfelder

- `id`
- `event_type`
- `resource`

## Antwortmodell

- `status`
- `reason`
- `verification_state`
- `replay_state`
- `routing_state`
- `doctrine_state`
- `receiver_runtime_state`

## Harte Ablehnungszustaende

- `missing_env_refs`
- `invalid_signature`
- `replay_suspected`
- `malformed_event`
- `unsupported_event_scope`
