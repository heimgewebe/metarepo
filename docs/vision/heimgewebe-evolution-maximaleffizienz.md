# Vision: Heimgewebe-Evolution (Maximaleffizienz)

> **Zustand heute:** Stabiler Kern, event-basiert, lokal.
> **Ziel:** Ein System, das **proaktiv** den **optimalen nächsten Schritt** vorschlägt.

## Phasen

### Welle 1: Konsolidierung & Basis-Agenten
- **Ziel:** Stabile Verträge, `wgx`-CLI als einziger Einstiegspunkt, Basis-Automatisierung.
- **Artefakte:**
  - `metarepo`: `contracts-v1` (final), Reusable-Workflows.
  - `wgx`: `doctor`, `metrics`, `fleet`, `knowledge`.
  - `hausKI`: Playbook-Runner, lokaler State, `heimlern`-Anbindung.
  - `semantAH`: Basis-Index über Vault/Code.
  - `chronik`: Ingest von `intent_event`/Rewards → semantAH.

### Welle 2: Proaktive Assistenz
- **Ziel:** Das System *antizipiert* den Nutzerwunsch und schlägt Aktionen vor.
- **Kern-Feature:** `/assist`-Endpoint in `hausKI`.
- **Technik:**
  - `mitschreiber`: liefert Echtzeit-Kontext (`os.context.intent`).
  - `semantAH`: Vektor-Index + Graph für Ähnlichkeitssuche.
  - `heimlern`: Policy `suggest_next_action(context)` → `(action, score)`.
  - `hausKI`:
    - Nimmt `/assist`-Request mit Kontext entgegen.
    - Fragt `heimlern` nach Vorschlägen.
    - Präsentiert Top-Vorschlag im `sichter`-UI.
- **Meilensteine:**
  1. Contracts für `/assist` & `suggest_next_action`.
  2. **Welle 2:** `/assist` in hausKI, Graph/Index in semantAH, Intents/Rewards in chronik/mitschreiber.
  3. `sichter`-UI zeigt Vorschläge an.
  4. Telemetrie: Acceptance-Rate der Vorschläge.

### Welle 3: Selbstoptimierung
- **Ziel:** Das System lernt aus Feedback und verbessert seine Vorschläge autonom.
- **Kern-Feature:** `heimlern`-Policies werden automatisch aktualisiert.
- **Technik:**
  - `sichter`: Feedback (`accept/reject/modify`) → `policy.feedback`-Event.
  - `heimlern`:
    - Konsumiert `policy.feedback`-Events.
    - Aktualisiert Policy-Parameter (z.B. via Online-Lernen/Bandits).
    - `wgx`-Job versioniert Policy-Snapshots in Git.
- **Meilensteine:**
  1. Feedback-Loop `sichter → heimlern` ist geschlossen.
  2. Policy-Snapshots werden automatisch versioniert.
  3. A/B-Tests für verschiedene Policy-Versionen.
