# Heimgeist vs. HausKI – funktionale Grenzziehung

## Heimgeist (Meta-Agent, Systembeobachter)

Heimgeist agiert auf der Ebene des gesamten Heimgewebes. Er liest Ereignisse (chronik), erkennt Muster, bewertet Risiken, interpretiert semantische Kontexte (semantAH) und stößt systemische Handlungen an.

Sein Fokus liegt auf:
- Konsistenzprüfung im Gesamtverbund
- Erkennen von Drift, Redundanzen, Brüchen
- Delegation von Aufgaben an passende Subsysteme
- Kontextualisierung und Reflexion von Ereignissen
- Auslösen von Guard/Smoke-Prüfungen über WGX

Heimgeist denkt über das System nach – nicht über das einzelne Problem.

---

## HausKI (lokaler Orchestrator und Inferenz-Motor)

HausKI arbeitet auf der Ebene der konkreten Interaktion. Er führt Modelle aus, orchestriert Inferenzpipelines, verwaltet lokalen Speicher (short-term, working context, long-term), führt RAG-Abfragen aus, steuert Audio-/Dev-Tools und interagiert direkt mit dem Nutzer.

Sein Fokus liegt auf:
- Ausführen von Assistenz-Anfragen
- Koordinieren lokaler Agents und Modelle
- Interpretieren von RAG-Graphen (semantAH)
- Dev-Assistenz (PR-Drafter, Lokaler Review)
- Offline-First-Policies, GPU-Scheduling

HausKI ist der aktive Motor – Heimgeist ist der systemweite Beobachter.

---

## Interaktion

1. Ereignisse laufen in chronik.
2. Heimgeist interpretiert.
3. Heimgeist entscheidet, was passieren soll.
4. HausKI entscheidet, wie es lokal ausgeführt wird.

Eine Trennung wie zwischen Regisseur (Heimgeist) und Ensemble (HausKI).
