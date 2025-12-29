# ADR-0029 CI Artifact Truth & First-Run Bootstrap Policy

Datum: 2025-12-28
Status: Accepted

## Kontext

Observatory-Artefakte (z.B. `knowledge.observatory.json`, `insights.daily.json`) sind epistemische Wahrheitsanker im Heimgewebe.

Die frühere CI-Logik vermischte zwei grundlegend verschiedene Zustände:
1.  **First-Run**: Es existiert noch kein Release (Initialzustand).
2.  **Fehlerfall**: Ein Release existiert, aber das Artefakt fehlt oder ist leer.

Bisherige Implementierungen nutzten oft "Silent Fallbacks" (stille Rückfallwerte), die eine epistemische Ehrlichkeit untergruben, indem sie fehlende Daten maskierten.

## Entscheidung

Wir legen folgende Regeln normativ fest:

### 1. Artifact Truth (Normalbetrieb)

Wenn ein Release existiert, gilt:
*   Die Artefakte **müssen** existieren.
*   Die Artefakte dürfen **nicht leer** sein.
*   Fehlen oder Leere führt zwingend zu **CI FAIL**.
*   Es gibt **keine stillen Fallbacks** in Production.

### 2. First-Run / Bootstrap

Wenn **kein** Release existiert:
*   Die CI darf explizit im **Bootstrap-Modus** laufen.
*   Dieser Modus muss für Menschen und Maschinen sichtbar geloggt werden (z.B. via `::notice:: First Run`).
*   Es darf kein stilles "Weiter so" geben; der Sonderstatus muss explizit sein.

### 3. Strict Mode (Runtime & Build)

Der **Strict Mode** definiert das Verhalten der Anwendung:
*   Keine Fixtures.
*   Keine Fake-Daten.
*   Ein leerer Zustand wird **explizit als leer** gerendert.
*   **Wichtig:** Strict Mode bedeutet nicht automatisch CI-Abbruch. Der CI-Abbruch hängt allein von der *Artifact Truth* ab (siehe Punkt 1), nicht von der UI-Darstellung.

## Konsequenzen

*   **Deterministische CI**: Die Pipeline verhält sich vorhersagbar basierend auf dem Vorhandensein valider Daten.
*   **Sichtbarer Bootstrap**: Der First-Run ist ein legitimer, aber deutlich markierter Sonderfall.
*   **Epistemische Ehrlichkeit**: Wir priorisieren die Korrektheit des Systemzustands über "grüne Builds".
*   **Leitstand-Verhalten**: Der Leitstand darf eine "leere Wahrheit" anzeigen (wenn keine Daten da sind), aber niemals eine "falsche Wahrheit" (Mock-Daten im Strict Mode).

## Abgrenzung

Diese ADR definiert die verbindlichen Regeln. Die technische Umsetzung erfolgt in den jeweiligen Komponenten und Workflows, unter anderem:
*   `knowledge-observatory-drift.yml`
*   `publish-insights-daily.yml`
*   `leitstand` (UI Empty State Handling)
*   `semantAH` (Produktion der Artefakte)

## Verweise

*   [ADR-0028: Leitstand Strict Build Symmetry](./0028-leitstand-strict-build-symmetry.md)
*   CI-Workflows: `knowledge-observatory-drift.yml`, `publish-insights-daily.yml`
