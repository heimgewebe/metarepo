# Fleet-Aufnahme: Konvergenzregelkreis v1

## Entscheidung

`heimgewebe/konvergenzregelkreis` wird als Core-Fleet-Repository in `fleet/repos.yml` aufgenommen.

## Begründung gegen die Aufnahmekriterien

- **Konkreter gemeinsamer Bedarf:** Das Repository besitzt versionierte Protokollschemas, Evidence-Profile R0–R3, Konformitätsfixtures und eine zustandslose Referenzauswertung. Diese Lieferflächen sind für Bureau-, Grabowski-, Systemkatalog-, Chronik- sowie Projektionsintegrationen vorgesehen.
- **Eindeutiger Name und Scope:** Der Konvergenzregelkreis bewertet ausschließlich, ob ein vorgelegtes Evidence-Paket einen definierten Übergang erfüllt. Er besitzt keinen Task-, Queue-, Lease-, Merge-, Deployment-, Runtime-, Fleet- oder Ereignisstatus.
- **Consumer-Auswirkung:** Die Aufnahme macht das Repository für gemeinsame Contract-, Prüf- und Driftwerkzeuge sichtbar. Sie ändert keinen bestehenden Consumer automatisch und ersetzt keine domäneneigene Wahrheit.
- **Nicht nur allgemeine Zugehörigkeit:** Der konkrete Fleet-Nutzen liegt in gemeinsamen versionierten Verträgen und Konformitätsprüfungen, nicht in der bloßen Sichtbarkeit im Ökosystem.

## Sicherheitsgrenze

Die Fleet-Aufnahme autorisiert keinen pauschalen Template-, Workflow- oder Contract-Rollout. Jeder Consumer übernimmt eine konkrete Protokollversion weiterhin über einen eigenen PR mit Kompatibilitäts-, Review- und Rückrollbeleg.

## Primärquelle

- Repository: `https://github.com/heimgewebe/konvergenzregelkreis`
- initiale öffentliche Version: `v0.1.0`
- initialer Commit: `de8b2733da57a27a94ff55ce79b04fc1dbe7835b`
