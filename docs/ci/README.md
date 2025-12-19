# CI Taxonomy

Dieses Dokument definiert die Klassifizierung von CI-Workflows im Heimgewebe, um Klarheit über Prioritäten und Erwartungshaltungen zu schaffen.

## 1. Guard (Blockierend)

Diese Workflows müssen **immer** grün sein. Ein Fehlschlag blockiert Merge/Release. Sie sichern die fundamentale Integrität des Repositories.

*   **Beispiele:**
    *   `ci.yml` (Unit Tests, Linter, Typprüfung)
    *   `wgx-guard.yml` (Basis-Validierung der WGX-Funktionalität)
    *   `fleet-check` (Konsistenz der Repo-Matrix)

## Fleet-Policy: WGX-Profil Erwartung (wichtig für fleet-check / repoLens)

Nicht jedes Repo braucht zwingend ein `.wgx/profile.yml`. Entscheidend ist, ob es **erwartet** wird.

**Quelle der Wahrheit:** `.ai-context.yml` (pro Repo) – Schlüssel:

Wichtig: `heimgewebe.fleet.enabled: true` allein impliziert **keine** WGX-Profilpflicht. Die Erwartung wird ausschließlich über die Felder unter `heimgewebe.wgx` gesteuert.

```yaml
heimgewebe:
  fleet:
    enabled: true|false
  wgx:
    profile_expected: true|false
    guard_smoke_expected: true|false
```

**Interpretation:**
- `profile_expected: true` → fehlendes `.wgx/profile.yml` ist ein echter Befund.
- `profile_expected: false` → fehlendes Profil ist Absicht (kein Befund).
- fehlt der Schlüssel → Erwartung ist *unklar* (repoLens darf warnen, aber soll eine Intentions-Deklaration empfehlen).

Damit bleibt die **Semantik (Policy)** in `.ai-context.yml`, während die **Motorik (Checks)** in WGX/repoLens lebt.

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
