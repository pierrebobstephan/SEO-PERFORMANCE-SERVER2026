# Bridge Plugin Suite Connection Model

## Verbindungsart

- keine offene Remote-API
- staging-only
- domain-bound
- packaged preview only

## Startverhalten

- Plugin liest `config/bridge-config.json`
- Plugin leitet daraus bound domain, expected URLs, default mode und stop conditions ab
- Plugin baut daraus lokale Connection-, Baseline- und Guardrail-Zustaende

## Gate

- Bridge Plugin Suite Connection Model: `approval_required`
