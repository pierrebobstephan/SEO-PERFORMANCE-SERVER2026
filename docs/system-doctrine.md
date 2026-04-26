# System Doctrine

## Status

Dieses Dokument ist die kanonische Langfassung der Systemdoktrin fuer das gesamte Suite- und Plugin-Projekt. Es ersetzt die bisherige v5-Leitbasis und leitet sich ab sofort aus [Doktrin04.04.2026-Version-8.0.txt](/opt/electri-city-ops/Doktrin04.04.2026-Version-8.0.txt) ab.

[AGENTS.md](/opt/electri-city-ops/AGENTS.md) bleibt die knappe, verbindliche Repo-Steuerdatei. Wenn zwischen Dokumenten Spannung entsteht, gilt immer die strengere Regel. Fuer dieses Repo haben Workspace-Grenzen, Betriebssystemschutz, Rocket-Cloud-Sperre, Approval-Pflicht, Validation und Rollback immer Vorrang.

## Dokumenttyp

Governance / Operations / Safety / Resilience / Ethics / AI Management / Agentic Security / SEO-GEO-Performance Doctrine

## Kanonische Quellenkette

- [AGENTS.md](/opt/electri-city-ops/AGENTS.md)
- [docs/system-doctrine.md](/opt/electri-city-ops/docs/system-doctrine.md)
- [Doktrin04.04.2026-Version-8.0.txt](/opt/electri-city-ops/Doktrin04.04.2026-Version-8.0.txt)
- [docs/doctrine-alignment-report.md](/opt/electri-city-ops/docs/doctrine-alignment-report.md)

Die TXT-Datei ist die normative 8.0-Quellfassung. Dieses Markdown-Dokument ueberfuehrt sie in repo-spezifische, technisch anschlussfaehige Leitregeln.

## Repo-Kerndoktrin

"Das Programm soll vollstaendig autonom, robust und defensiv-schuetzend arbeiten, dauerhaft aus seinen Daten lernen und sich selbst optimieren. Es verbessert Performance, Struktur und Ressourcennutzung kontinuierlich, erkennt Fehler automatisch und korrigiert sie eigenstaendig. Alle internen Module arbeiten harmonisch zusammen und tauschen Wissen aus. Selbstverbesserungen am Code erfolgen ausschliesslich sicher, validiert und ohne Risiko fuer das Betriebssystem. Ziel ist ein stabiles, lernfaehiges und selbstheilendes System, das sich langfristig weiterentwickelt."

## Integrierte 8.0-Kernpunkte

### Oberste Leitformel

- So autonom wie sicher moeglich.
- So defensiv wie betrieblich noetig.
- So begrenzt wie das Risiko es verlangt.
- So beobachtbar wie Vertrauen es fordert.
- So reversibel wie die Realitaet es erfordert.
- So erklaerbar wie Menschen, Auditoren und Regulatoren es benoetigen.
- So resilient wie Stoerungen, Angriffe und Marktveraenderungen es verlangen.
- So ethisch wie Menschenwuerde, Grundrechte und Gesellschaft es erwarten.
- So daten- und evidenzgebunden wie Wahrheit, Nachvollziehbarkeit und Provenance es verlangen.
- So agentisch wie Kontrolle, Tool-Grenzen und Audit-Ketten es erlauben.
- So generativ wie Belegbarkeit, Herkunft und Nicht-Taeuschung es zulassen.
- So semantisch differenzierend wie globale Such-, Antwort- und Generatorsysteme es erfordern.

### Absolute Prioritaetenordnung

1. Menschenwuerde, Grundrechte und koerperliche Unversehrtheit
2. Sicherheit, Missbrauchsvermeidung und Schutz vor realem Schaden
3. Wahrhaftigkeit, Nicht-Taeuschung und Integritaet von Aussagen, Daten und Beweisen
4. Systemintegritaet, Vertrauensgrenzen und sichere Zustandskontrolle
5. Containment, Blast-Radius-Begrenzung und sichere Degradation
6. Menschliche Steuerung, Freigabehoheit und Uebersteuerbarkeit
7. Validierung, Verifikation und Reproduzierbarkeit
8. Wiederherstellbarkeit, Rollback und Recovery-Faehigkeit
9. Beobachtbarkeit, Auditierbarkeit und Erklaerbarkeit
10. Datenschutz, Datensouveraenitaet und Zweckbindung
11. Fairness, Nicht-Diskriminierung und gesellschaftliche Verhaeltnismaessigkeit
12. Nachhaltigkeit, Ressourcenverantwortung und Kostenkontrolle
13. Semantische Klarheit, Wissensraum-Kompatibilitaet und Zitierfaehigkeit
14. Adaptive Optimierung und lernfaehige Verbesserung
15. Performance, Sichtbarkeit und Wachstum
16. Geschwindigkeit
17. Bequemlichkeit

### Nicht verhandelbare Axiome

- Sicherheit vor Tempo
- Begrenzung vor Ambition
- Beobachten vor Handeln
- Kein Nachweis, keine Aenderung
- Fail closed, niemals fail open
- Minimal-Power-Prinzip
- Reversibilitaet ist Pflicht
- Menschliche Freigabe bleibt oberste Instanz, wo Risiko oder externe Wirkung relevant sind
- Lernen ist der Validierung untergeordnet
- Grenzen sind real: Rollen-, Tenant-, Netzwerk-, Secret-, Daten-, Tool- und Rechtsgrenzen
- Zero Trust ist Grundhaltung
- Explainable by default
- Ethik ist Hard Constraint
- Praediktion dient Praevention, nicht Aggression
- Autonomie ohne Budget, Guardrails und Not-Aus ist verboten
- Provenance ist Pflicht, ersetzt aber nie Wahrheit
- Kundensysteme und Livesysteme sind keine Experimentierflaechen
- Supply Chain ist Teil der Sicherheitsgrenze

## Formale 8.0-Pflichten

### AI-Management-System

Die Suite unterliegt ab jetzt explizit einer AI-Management-System-Schicht. Verantwortlichkeiten, Freigabekompetenzen, Risikoappetit, Kontrollziele, Review-Zyklen und Korrekturmassnahmen muessen dokumentiert und auditierbar bleiben.

### Pflichtinventar

Kein AI-System, Agent, Tool-Runner oder externer Write-Pfad darf produktiv oder kundennah betrieben werden, ohne im AI-Systemregister gefuehrt zu sein. Mindestens zu fuehren sind:

- Systemname, Version, Owner, Validator, Operator, Auditor
- Zweck, Scope, Rechtsraum, betroffene Personen oder Gruppen
- Risikoklasse und Kritikalitaet
- Datenklassen, Quellen, Loeschbarkeit und Rechtsgrundlage
- Modell-, Prompt-, Policy-, Memory- und Tool-Layer
- Write-Faehigkeiten, Connectoren, Monitoring, Kill-Switch, Fallback und Rollback

### Risikoklassen

- `R0`: Observe / Assist
- `R1`: Bounded Automation
- `R2`: Controlled Externality
- `R3`: High Trust Required
- `R4`: Critical / Sovereign

Je hoeher die Klasse, desto strenger muessen Freigabe, Explainability, Logging, Human Oversight, Red-Teaming, Recovery und Deployment-Grenzen sein.

### Verbindlicher Lebenszyklus

Jedes System folgt:

`govern -> register -> classify -> assess -> design -> source_verify -> build -> simulate -> validate -> approve -> deploy -> monitor -> re_evaluate -> learn -> decommission -> archive_delete`

Abkuerzungen an Register, Risikoklassifizierung, Impact-Assessment, Baseline, Rollback, Validierung, Monitoring oder Dokumentation sind nicht zulaessig.

### Pflicht-Impact-Assessment

Vor erstmaliger Nutzung und vor jeder wesentlichen Aenderung ist ein Impact-Assessment zu erstellen. Es muss Auswirkungen auf Individuen, Gruppen, Missbrauch, Datenschutz, Fehlanreize, Drift, Halluzination, Tool-Missbrauch, Skalierungsrisiken und Recovery-Pfade betrachten.

### Daten-, Retrieval- und Provenance-Governance

- Daten muessen klassifiziert werden
- Herkunft, Lizenzstatus, Aktualitaet, Zweckbindung, Bias- und Toxizitaetsrisiken muessen dokumentiert sein
- Retrieval-Quellen brauchen Trust-Klassen, Provenance, Scope-Isolation und Poisoning-Kontrollen
- Herkunft, Evidenz und Unsicherheit sind getrennt auszuweisen

### Modell-, Prompt-, Policy-, Memory- und Agenten-Governance

Doktrin 8.0 verlangt getrennte Steuerung fuer:

- Model Layer
- Policy Layer
- Prompt Layer
- Memory Layer
- Tool Layer
- Agent Layer

Kein Agent darf ausserhalb explizit freigegebener Aktionsraeume handeln.

## Repo-spezifische harte Grenzen

- Keine Aenderungen ausserhalb `/opt/electri-city-ops`
- Keine Aenderungen an Rocket Cloud
- Keine externen Schreibzugriffe ohne Approval
- Keine globale oder ungebundene Aktivierung
- Default bei Unsicherheit ist `observe_only`
- Reale externe Wirkung bleibt mindestens `approval_required`, haeufig `observe_only`
- `apply -> validate -> rollback` ist Pflicht
- Generierter Code bleibt untrusted, bis Tests, Policy-Checks, Validierung und Rollback-Pfad vorliegen

## Explizite Zustaende

Die Doktrin 8.0 fuehrt und bestaetigt mindestens diese Zustaende:

- `observe_only`
- `safe_mode`
- `controlled_apply`
- `containment_mode`
- `rollback_mode`
- `self_healing_active`
- `emergency_freeze`
- `adaptive_resonance_mode`
- `centaur_mode`
- `blueprint_ready`
- `approval_required`
- `pilot_ready`
- `active_pilot`
- `stable_applied`
- `degraded_safe`
- `blocked`
- `rollback_required`

## Verbindlicher Betriebszyklus im Repo

Fuer dieses Repo bleibt die knappe Betriebsform:

`observe -> analyze -> decide -> simulate -> apply -> validate -> learn -> document`

Die 8.0-Langform ist zusaetzlich verbindlich, wo Daten-, Agenten-, Provenance-, Lieferketten-, Modell-, Retrieval- oder Post-Deployment-Governance betroffen sind.

## Akzeptanzstandard fuer Aenderungen

Keine relevante Aenderung gilt als erfolgreich ohne:

- dokumentierten Before-State
- expliziten Zweck
- definierten Scope
- Risikoklasse
- Impact-Assessment, wenn relevant
- messbare Zielmetriken
- definierte Abort-Kriterien
- glaubwuerdigen Rollback- oder Containment-Pfad
- definierte Validierung
- Post-Change-Evidenz
- nachvollziehbare Dokumentationsspur
- Erklaerbarkeits- und Provenance-Nachweis, wenn relevant

## Umsetzungsstatus im Repo

Die Suite ist jetzt auf 8.0 als Fundament umgestellt. Technisch durchgesetzt werden bereits:

- neue kanonische Quellenkette
- 8.0-Policy-Version
- AI-Management- und Lifecycle-Felder in der Doctrine-Policy
- Risikoklassen `R0` bis `R4`
- erweiterte Simulation mit Impact- und Evidence-Feldern
- Gate-Checks fuer Register-, Impact-, Provenance-, Supply-Chain- und Human-Oversight-Bereitschaft

Die restliche operative Angleichung wird in [docs/doctrine-alignment-report.md](/opt/electri-city-ops/docs/doctrine-alignment-report.md) nachgehalten.

Seit dem 8.0-Umbau liegen zusaetzlich konkrete Governance-Artefakte vor:

- [config/ai-system-register.json](/opt/electri-city-ops/config/ai-system-register.json)
- [config/ai-impact-assessments.json](/opt/electri-city-ops/config/ai-impact-assessments.json)
- [config/provenance-evidence.json](/opt/electri-city-ops/config/provenance-evidence.json)
- [config/supply-chain-evidence.json](/opt/electri-city-ops/config/supply-chain-evidence.json)

Diese Artefakte werden ueber die lokale Suite-Validation, die Local Console und die globale Productization-Readiness mitgeprueft.
