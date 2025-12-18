# CI Taxonomy

Dieses Dokument definiert die Klassifizierung von CI-Workflows im Metarepo, um Klarheit über Prioritäten und Erwartungshaltungen zu schaffen.

## 1. Guard (Blockierend)

Diese Workflows müssen **immer** grün sein. Ein Fehlschlag blockiert den Merge oder das Release. Sie sichern die fundamentale Integrität des Repositories.

*   **Beispiele:**
    *   `ci.yml` (Unit Tests, Linter, Typprüfung)
    *   `wgx-guard.yml` (Basis-Validierung der WGX-Funktionalität)
    *   `fleet-check` (Konsistenz der Repo-Matrix)

## 2. Advisory (Warnend)

Diese Workflows liefern wichtige Signale, blockieren aber nicht zwingend den Fortschritt, wenn sie fehlschlagen (z.B. bei externen Flaps oder nicht-kritischen Metriken).

*   **Beispiele:**
    *   `linkcheck.yml` (Prüfung auf tote Links – kann False Positives enthalten)
    *   `impact-analysis` (Informativer Graph über Auswirkungen von Änderungen)
    *   `fleet-doctor` (Gesundheitszustand der gesamten Flotte – kann durch externe Faktoren rot sein)

## 3. Heavy (Opt-in / Nightly)

Ressourcenintensive oder langlaufende Tests, die nicht bei jedem Commit ausgeführt werden.

*   **Beispiele:**
    *   `e2e` (End-to-End Tests über mehrere Container/Services hinweg)
    *   `smoke` (Erweiterter Integrationstest)
    *   `net-probe` (Netzwerk-Diagnose)

## Governance

Neue Workflows müssen einer dieser Kategorien zugeordnet werden. "Guard"-Workflows sollten schnell (< 5 Min) und deterministisch sein.
