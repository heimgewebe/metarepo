# Vision: Heimgewebe – Epistemische Autopoiesis (Blaupause)

> **Status:** Vision / Blueprint
> **Reference:** [Docs: Principles - Epistemische Autopoiesis](../principles/epistemic-autopoiesis.md)
> **Ziel:** System-Selbstreflexivität & Kognitive Reife

## 1. Vision & Zweck

Dieses Dokument beschreibt die evolutionäre Blaupause für die Transformation des Heimgewebes von einer technischen Orchestrierungsplattform zu einem **kognitiv reifen, selbstkorrigierenden Organismus**.

Das Ziel ist **Epistemische Autopoiesis**: Die Fähigkeit des Systems, seine eigenen Denkstrukturen zu erhalten, zu überprüfen und zu korrigieren.

---

## 2. Repo-Rollen (Epistemische Funktion)

Im Kontext der epistemischen Autopoiesis übernehmen die Repositories spezifische kognitive Rollen innerhalb des Organismus:

### `metarepo` (Die Verfassung)
*   **Rolle:** Single Source of Epistemic Truth.
*   **Funktion:** Beherbergt die Contracts (`contracts/epistemic/`) und Prinzipien (`docs/principles/`), die gültiges Denken definieren.
*   **Verhalten:** Agiert als "Über-Ich", definiert Normen (was erlaubt ist) und das Idealbild (Blaupause).

### `chronik` (Das Epistemische Log)
*   **Rolle:** Die unveränderliche Geschichte des Denkens.
*   **Funktion:** Speichert alle epistemischen Events (`decision.preimage`, `event.contradiction`, `event.reflection.request`).
*   **Verhalten:** Neutral. Bewertet nicht, erinnert nur. Stellt sicher, dass kein Gedanke verloren geht oder heimlich geändert wird.

### `semantAH` (Der Mustererkenner)
*   **Rolle:** Das unterbewusste Monitoring.
*   **Funktion:** Erkennt `concept.drift`, clustert Widersprüche und identifiziert wiederholte epistemische Warnungen (`insight.epistemic.pattern`).
*   **Verhalten:** Aggregiert Einzelwarnungen zu systemischen Mustern. Transformiert "Einzelfehler" in "strukturelle Diagnosen".

### `hausKI` (Die Exekutive)
*   **Rolle:** Der bewusste Akteur.
*   **Funktion:** Trifft Entscheidungen basierend auf Kontext.
*   **Neue Macht:** Hat das **Recht zu verweigern** oder zu **de-priorisieren**, wenn:
    *   Alternativen fehlen.
    *   Unsicherheiten verschwiegen werden.
    *   Reflexionsfenster ignoriert werden.
*   **Verhalten:** Erzwingt normative Autopoiesis, indem die Konfidenz von `weak` Entscheidungen gesenkt wird.

### `heimlern` (Die Lernschleife)
*   **Rolle:** Der Korrekturmechanismus.
*   **Funktion:** Analysiert Fehlannahmen.
*   **Verhalten:** Wandelt `event.contradiction` in Lern-Updates um. Stellt sicher, dass das System den gleichen epistemischen Fehler nicht zweimal macht.

### `leitstand` (Der Ehrliche Spiegel)
*   **Rolle:** Die Schnittstelle zur Realität.
*   **Funktion:** Visualisiert die "Epistemische Gesundheit".
*   **Verhalten:** Zeigt explizit:
    *   Offene Unsicherheiten (alternd!).
    *   Aktive Widersprüche.
    *   Driftende Konzepte.
    *   **Kein "Alles Grün" Dashboard:** Weigert sich, die Unordentlichkeit der Realität zu verstecken.

---

## 3. Der evolutionäre Pfad (Eskalationsstufen)

Die Implementierung folgt einer klaren Reifekurve, von Sichtbarkeit bis zur Normsetzung.

### Phase 0: Verfassung (Implementiert)
*   **Fokus:** Definition & Bewusstsein.
*   **Artefakte:** Prinzipien-Dokument, ADR, Schemata, Warn-only Guard.
*   **Effekt:** Das System "weiß", wie gutes Denken aussieht, handelt aber noch nicht danach.

### Stufe 1: Warn-Autopoiesis (Sichtbarkeit)
*   **Fokus:** Das Unsichtbare sichtbar machen.
*   **Mechanismus:** `wgx-guard` scannt nach fehlenden Kontexten. `semantAH` beginnt Tracking von `uncertainty` und `drift`.
*   **Effekt:** Entwickler sehen "Gelbe Ampeln" (Warnungen) in PRs. Ignoranz wird zur Entscheidung, nicht mehr zum Standard.

### Stufe 2: Epistemic Memory (Gedächtnis)
*   **Fokus:** Historisierung von Verhalten.
*   **Mechanismus:** `warning.memory` trackt, wie oft spezifische Repos oder Agenten epistemische Standards verletzen.
*   **Effekt:** Das System hört auf, jeden Fehler als neues Ereignis zu behandeln. Es erkennt "Wiederholungstäter" (z.B. "Dieses Repo dokumentiert nie Entscheidungen").

### Stufe 3: Reflexion (Dialog)
*   **Fokus:** Dialog.
*   **Mechanismus:** **Reflexionsfenster**.
*   **Logik:** Wenn ein Muster stabil ist (z.B. >3 Warnungen), triggert das System einen `event.reflection.request`.
*   **Effekt:** Das System fragt "Warum?". Es verlangt eine Begründung für die Abweichung.

### Stufe 4: Normative Autopoiesis (Reife)
*   **Fokus:** Qualitätsunterscheidung.
*   **Mechanismus:** **Epistemic Quality** (`grounded` vs. `weak`).
*   **Logik:** Entscheidungen, die trotz offener Reflexionsanforderung getroffen werden, werden als `weak` markiert.
*   **Effekt:** `weak` Entscheidungen sind formal gültig, aber de-priorisiert. Das System bevorzugt strukturell fundierte Handlungen. Dies ist der "Kipppunkt", an dem das System seine Integrität über blinde Ausführung stellt.

---

## 4. Zentrale Epistemische Objekte

### Decision Archaeology
Entscheidungen sind keine Punkt-Ereignisse, sondern historische Artefakte.
*   **Anforderung:** Jede Entscheidung braucht ein `decision.preimage`.
*   **Inhalt:** Annahmen, verworfene Alternativen, bekannte Unsicherheiten.
*   **Ziel:** Späteres Debugging ermöglichen, *warum* wir dachten, das sei eine gute Idee.

### Uncertainty as a First-Class Object
Ungewissheit wird verwaltet, nicht versteckt.
*   **Lifecycle:** `discovered` -> `acknowledged` -> `deferred` -> `reduced` -> `reframed` -> `obsolete`.
*   **Regel:** Automation darf Ungewissheit nie "auto-schließen". Nur neue Evidenz kann sie schließen.

### Contradiction as Signal
Dissens ist ein Diagnoseinstrument.
*   **Event:** `event.contradiction`.
*   **Aktion:** Triggert einen `context.check`, keinen Fehler.
*   **Philosophie:** Ein System ohne Widersprüche halluziniert wahrscheinlich Konsistenz.

### Concept Drift
Bedeutungen ändern sich. Das System beobachtet diesen Wandel.
*   **Event:** `event.semantic.concept.drift`.
*   **Aktion:** Wenn ein Begriff (z.B. "Agent") in zwei Repos unterschiedliche Dinge bedeutet, flaggt `semantAH` dies.

---

## 5. Verdichtete Essenz

Heimgewebe wird kein System, das "immer recht hat".
Es wird ein System, das **weiß, warum es glaubt, was es glaubt** – und wann es aufhören sollte, es zu glauben.

Es ist der Wandel von **Automatisierter Ausführung** zu **Reflektierter Kognition**.
