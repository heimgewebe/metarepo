# End-to-End: aussensensor → chronik → heimlern

> **Ziel:** Nachweis, dass ein Außen-Event korrekt eine Policy-Anpassung triggert.

## Setup
- **aussensensor**: lauscht auf `aussen.event` (z.B. via `POST /ingest/aussen`)
- **chronik**: persistiert Events, `heimlern` ist Consumer
- **heimlern**: Policy `demo-policy-aussen` (reagiert auf `aussen.event.score > 0.8`)
- **hausKI**: orchestriert, nutzt `heimlern`

## Ablauf
1. `just e2e.reset`
2. Event simulieren:
   ```bash
   just e2e.aussen-event score=0.9 content="Test-Event"
   ```
3. Logs prüfen:
   - `aussensensor` loggt Event-Empfang & -Export.
   - `chronik` loggt Ingest.
   - `hausKI` loggt Policy-Aufruf & Entscheidung.
   - `heimlern` loggt `reward()`-Aufruf.
4. Report prüfen:
   - Report: `./.hauski-reports/<timestamp>-e2e-aussen-chronik-heimlern.md`
   - Inhalt: Event, Policy-Entscheidung, Reward-Kalkulation.

## Erwartetes Ergebnis
- Policy-Parameter in `heimlern` wurden angepasst.
- Report enthält alle Schritte mit korrekten Werten.
