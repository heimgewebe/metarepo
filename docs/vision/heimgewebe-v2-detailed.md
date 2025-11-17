# Heimgewebe v2 – Detaillierte Vision

> **Fokus:** `assist`-Loop (Kontext → Vorschlag → Aktion)

## Komponenten & Rollen (v2)

| Komponente | Rolle in v2 | Wesentliche Änderung |
| --- | --- | --- |
| **mitschreiber** | Primär-Sensor (Intent) | Erzeugt `os.context.intent` aus UI/OS-Events |
| **chronik** | Ingest/Drehscheibe | Normalisiert, versioniert, leitet weiter |
| **semantAH** | Semantischer Index | Vektor-DB + Graph; `/embed`, `/similar` |
| **hausKI** | Assistenz-API | `/assist(context)`-Endpoint, Job-Runner |
| **heimlern** | Vorschlags-Policy | `suggest_next_action(context)`-Modell |
| **sichter** | Interaktions-UI | Zeigt Vorschläge, sammelt Feedback |
| **wgx** | System-Bus | `wgx agent run ...`, `wgx knowledge ...` |

## User-Story: Proaktive Code-Hilfe

1.  **User-Aktion:** Entwickler:in arbeitet an `feature/xyz` in `hausKI`, öffnet `lib.rs`.
2.  **Kontext-Erfassung (`mitschreiber`):**
    -   `active_window`: `.../hausKI/src/lib.rs`
    -   `git_branch`: `feature/xyz`
    -   `recent_files`: `[.../playbook.yml]`
    -   → `os.context.intent` mit Payload.
3.  **Ingest (`chronik`):** Event wird validiert, persistiert.
4.  **Trigger (`hausKI`):** `hausKI` (oder ein `sichter`-Client) ruft `/assist` mit dem Kontext auf.
5.  **Vorschlags-Generierung (`hausKI` → `heimlern`):**
    -   `hausKI` fragt `heimlern`: `suggest_next_action(context)`.
    -   `heimlern` nutzt eine Policy (z.B. ein trainiertes Modell), die gelernt hat:
        > „Wenn `lib.rs` und `playbook.yml` zusammen editiert werden, ist der nächste Schritt oft `wgx agent run test_playbook`“.
    -   `heimlern` retourniert: `[{"action": "wgx agent run test_playbook", "score": 0.92}]`.
6.  **Anzeige (`sichter`):**
    -   UI zeigt an: „Vorschlag: `wgx agent run test_playbook` ausführen? [Ja] [Nein]“.
7.  **Feedback-Loop:**
    -   User klickt [Ja].
    -   `sichter` sendet `policy.feedback`-Event mit `{"reward": 1.0}`.
    -   `heimlern` konsumiert das Feedback und verstärkt die entsprechende Regel.

## Event-Flow (detailliert)

1.  Audio-Notiz → hausKI-audio → **Intent** (+ Transkript) → `intent_event` → **chronik**
2.  chronik validiert/normalisiert → schreibt Event → **semantAH** indiziert Transkript & Kanten
3.  **UI/Client** (z.B. `sichter`) pollt `chronik` oder `semantAH` für neue Intents
4.  UI zeigt Intent → User bestätigt/modifiziert → `/assist`-Request an **hausKI**
5.  `hausKI` → `heimlern` → Vorschlag → UI
6.  User-Feedback → `policy.feedback`-Event → `heimlern` lernt

## Meilensteine (Wave-2)

-   **Wave-2.1:** Contracts für `os.context.intent`, `policy.feedback`.
-   **Wave-2.2:** `mitschreiber`-Prototyp (macOS/Linux).
-   **Wave-2.3:** `/assist`-Endpoint (hausKI), semantAH Graph-Edges, chronik Intent-Ingest
-   **Wave-2.4:** `sichter`-UI für Vorschläge & Feedback.
-   **Wave-2.5:** `heimlern`-Policy `suggest_next_action`.
