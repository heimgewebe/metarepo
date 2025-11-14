# ADR-0002: Umbenennung von `leitstand` zu `chronik` und Einführung eines UI-Repos

- **Status**: Akzeptiert
- **Datum**: 2025-11-14
- **Kontext**:
  - Das bisherige `leitstand`-Repo hatte eine Doppelrolle: Es war sowohl für den Event-Ingest und die Persistenz (als Backend) zuständig als auch als Platzhalter für das zukünftige UI/Dashboard gedacht.
  - Diese semantische Überladung führte zu Unklarheiten. Das "Gedächtnis" des Systems (Event-Store) wurde begrifflich mit dem "Kontrollraum" (Dashboard) vermischt.
- **Entscheidung**:
  1.  Das bestehende Backend-Repository `leitstand` wird in `chronik` umbenannt.
      -   **`chronik`**: Verantwortlich für Event-Ingest, Persistenz und Audit-Trails. Dies ist das "Gedächtnis".
  2.  Ein neues Repository `leitstand` wird für das UI/Dashboard angelegt.
      -   **`leitstand`**: Verantwortlich für die Visualisierung von Daten aus `chronik`, `semantAH` und `hausKI`. Dies ist der "Kontrollraum".
- **Konsequenzen**:
  - **Vorteile**:
    -   **Klarheit**: Die Namen spiegeln die tatsächliche Funktion wider. `chronik` für historische Daten, `leitstand` für die Steuerung und Übersicht.
    -   **Saubere Trennung**: Die Trennung in zwei Repositories ermöglicht eine unabhängige Entwicklung von Backend und Frontend.
    -   **Verbesserte Architektur**: Das Schichtenmodell des Heimgewebes wird klarer und konsistenter.
  - **Nachteile**:
    -   **Aufwand**: Umbenennungen erfordern Anpassungen in der gesamten Codebasis, in CI-Workflows und in der Dokumentation.
    -   **Temporäre Inkonsistenz**: Während der Umstellung können vorübergehend veraltete Referenzen bestehen bleiben.
- **Betroffene Repos**:
  - `metarepo` (Dokumentation, `repos.yml`)
  - Alle anderen Repos, die auf `leitstand` verweisen (in Docs, CI, `.ai-context.yml`).