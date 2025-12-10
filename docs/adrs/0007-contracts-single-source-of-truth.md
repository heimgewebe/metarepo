# ADR-0007 Contracts als Single Source of Truth

Status: accepted
Datum: 2025-12-05
Betroffene Repos:
- heimgewebe/metarepo
- heimgewebe/aussensensor
- heimgewebe/chronik
- heimgewebe/semantAH
- heimgewebe/heimlern
- heimgewebe/hausKI
- heimgewebe/sichter
- heimgewebe/contracts (als Werkzeug- bzw. Spiegel-Repo)

---

## 1. Kontext

Heimgewebe nutzt in mehreren Repos JSON-Schemas und andere Contracts, zum Beispiel:

- `aussen.event.schema.json` für externe Ereignisse (aussensensor → chronik → heimlern),
- Policy-Contracts für heimlern,
- Wissens- und Index-Contracts (semantAH, hausKI),
- weitere Domain-Schemas.

Historisch sind Contracts an mehreren Stellen gleichzeitig aufgetaucht:

- im `metarepo` unter `contracts/`,
- im separaten Repo `heimgewebe/contracts`,
- als Kopien in Domain-Repos (z. B. `aussensensor/contracts/`, `chronik/docs/`).

Das führt zu typischen Drift-Risiken:

- Gleiche Datei-Namen mit unterschiedlicher Struktur,
- lokale „Fixes“ am Schema, die nie zurück in die Quelle gemeldet werden,
- Tools und KIs wissen nicht mehr, welches Schema „offiziell“ ist.

Gleichzeitig ist das metarepo bereits die faktische Control-Plane von Heimgewebe
und enthält:

- zentrale `contracts/*.schema.json`,
- Doku zu Contracts,
- CI-Workflows zur Contract-Validierung.

Diese Realität soll jetzt formalisiert werden.

---

## 2. Entscheidung

**2.1 Single Source of Truth**

1. **Alle Domain-Contracts von Heimgewebe werden fachlich im `metarepo` gepflegt.**
   Kanonische Quelle:
   `heimgewebe/metarepo/contracts/*.schema.json`

2. **Alle anderen Contract-Dateien in anderen Repos gelten als _Artefakte_ dieser Quelle.**
   Beispiele:
   - `heimgewebe/aussensensor/contracts/aussen.event.schema.json`
   - `heimgewebe/chronik/docs/aussen.event.schema.json`

3. **Diese Artefakte dürfen nicht mehr direkt geändert werden.**
   Jede fachliche Änderung an einem Contract muss über einen PR im `metarepo`
   erfolgen und von dort aus synchronisiert werden.

**2.2 Rolle des `heimgewebe/contracts` Repos**

4. Das Repo `heimgewebe/contracts` verliert die Rolle einer eigenständigen fachlichen Quelle.
   Es wird künftig:
   - entweder als reines Tooling-/Mirror-Repo genutzt (z. B. Ajv-CLI, Prototypen),
   - oder langfristig archiviert.

5. Falls es weiterhin aktiv genutzt wird, dürfen seine Contracts nur noch
   automatisiert aus dem `metarepo` synchronisiert werden (kein Direkt-Edit).

**2.3 Sync-Mechanik**

6. Im `metarepo` wird ein Script `scripts/contracts-sync.sh` eingeführt, das
   Contracts von `metarepo/contracts/` in definierte Zielpfade anderer Repos
   spiegelt.

7. Die Zuweisung „Quelle → Ziel(e)“ ist explizit im Script konfiguriert
   (Mapping-Tabelle). Neue Contracts müssen dort eingetragen werden.

8. Mediumfristig sollen CI-Workflows (z. B. `contracts-validate`) in Domain-Repos
   sicherstellen, dass lokale Kopien identisch zur Quelle sind (Drift-Check).

---

## 3. Begründung

**Klarheit**
Es gibt künftig genau eine Stelle, an der fachliche Änderungen an Contracts
verhandelt werden: PRs gegen `metarepo/contracts`.
Alle anderen Kopien sind davon abgeleitet und können mechanisch ersetzt werden.

**Wartbarkeit**
KIs, Tools und Menschen müssen nicht mehr raten, welches Schema „stimmt“.
„Zeig mir das Contract-Schema“ heißt: „schau in `metarepo/contracts/`“.

**Automatisierung**
Mit der Single-Source-Entscheidung wird es möglich, Drift automatisiert zu
erkennen und zu verhindern:

- einfache Checks „lokale Kopie = Byte-gleich zur Quelle?“,
- generierte Kommentare `// GENERATED FROM ...`,
- Sync-Tasks über `wgx` oder CI.

**Abgrenzung von Tooling**

Das separate `contracts`-Repo kann weiterhin für Dinge wie:

- experimentelle Tooling-Pipelines,
- CI-Jobs, die nur Contracts betreffen,
- Prototypen mit ajv/Buf/Redoc

genutzt werden – aber es bestimmt nicht mehr den fachlichen Stand der Contracts.

---

## 4. Konsequenzen

**4.1 Kurzfristig**

- Änderungen an Contracts müssen im `metarepo` erfolgen.
- Domain-Repos, die lokale Kopien halten, müssen einmalig auf die neue Quelle
  eingeschwenkt werden:
  - Dateien durch Sync aus `metarepo/contracts` ersetzen,
  - ggf. Warnkommentare „GENERATED – DO NOT EDIT“ hinzufügen.

**4.2 Mittelfristig**

- Einbindung von Drift-Checks in Domain-Repos:
  „Falls lokale Contract-Datei != Quelle → CI schlägt fehl.“
- Dokumentation anpassen:
  - `docs/contracts/contracts-index.md` im metarepo,
  - Hinweise in den READMEs von Domain-Repos (wo erfolgt die Pflege?).

**4.3 Langfristig**

- Optionales „Downgrade“ von `heimgewebe/contracts` zu:
  - Mirror-Repo (nur automatisiert befüllt),
  - oder Archiv-Repo (read-only).

---

## 5. Alternativen

1. **`contracts`-Repo als Master behalten**
   – würde bedeuten, Doku und bestehende Praxis im metarepo umzubauen und
   die Control-Plane zu verschieben.
   → Verworfen, da metarepo bereits natürliche Steuer-Ebene ist.

2. **Alles in Domain-Repos lassen**
   – jedes Repo pflegt „sein“ Contract-Schema lokal.
   → Verworfen, weil Drift und Inkonsistenzen vorprogrammiert sind.

3. **Verzicht auf formale Contracts**
   – rein implizite Contracts über Code und Tests.
   → Verworfen, weil Heimgewebe explizit auf Contract-Denken setzt.

---

## 6. Umsetzung

1. Dieses ADR einchecken.
2. `scripts/contracts-sync.sh` einchecken (siehe Patch).
3. Für erste wichtige Contracts (z. B. `aussen.event`) Zielpfade definieren
   und Sync testen.
4. Nach und nach:
   - Domain-Repos umstellen,
   - CI-Checks ergänzen,
   - `heimgewebe/contracts`-Repo in Doku neu verorten.

---

## 7. Notizen

- Dieses ADR beschreibt zunächst die Prinzipien.
  Konkrete Mappings (welches Schema geht in welches Repo) leben im Script
  und können dort iterativ ergänzt werden.
