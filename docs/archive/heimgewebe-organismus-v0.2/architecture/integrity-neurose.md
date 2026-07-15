# Integritätsneurose im Heimgewebe

**Architektur · Rollen · Invarianten (normativ)**

## 0. Zweck und Geltung

Dieses Dokument verankert die **Integritätsneurose** als bewusstes, dauerhaftes **Design- und Haltungsprinzip** des Heimgewebe-Organismus.

Ziel ist **nicht Stabilität im Sinne von Ruhe**, sondern **Stabilität durch früh sichtbare Irritation**.

> Wenn sich Integrität ruhig anfühlt, ist sie bereits falsch.

Dieses Dokument ist **normativ** für alle Repositories, Werkzeuge, CI-Mechaniken und KI-Agenten im Heimgewebe.

---

## 1. Axiome (nicht verhandelbar)

1. Transport ist unzuverlässig.
2. Artefakte sind wahrer als Events.
3. Pull schlägt Push.
4. Stille ist gefährlicher als Fehler.
5. Heilung ohne Markierung ist Lüge.

Aus diesen Axiomen folgt zwangsläufig die Integritätsneurose.

---

## 2. Kanonischer Wahrheitsanker

### 2.1 Artefakt

Der **einzige kanonische Wahrheitsanker** für Integrität ist:

```
reports/integrity/summary.json
```

veröffentlicht als **Release Asset** unter dem festen Tag:

```
integrity
```

Eigenschaften:

* eindeutig adressierbar
* versioniert
* historisch rekonstruierbar
* unabhängig von Event-Zustellung

**Events sind niemals Wahrheit.**

---

## 3. Pull-First-Architektur

### 3.1 Primärer Loop

```
Repo
 └─▶ Release Asset (summary.json)
         └─▶ Chronik (Pull)
                └─▶ Leitstand (Beobachtung)
```

Der Integritätsloop ist **pull-basiert**.
Alles andere ist **optional**.

### 3.2 Events

Das Event

```
integrity.summary.published.v1
```

ist:

* Hinweis
* Beschleuniger
* Opportunist

Es ist **nicht**:

* zuverlässig
* kritisch
* wahrheitsstiftend

---

## 4. Rollen der Repositories (verbindlich)

### semantAH — *Strikter Produzent*

**Rolle**

* Erzeugung der Wahrheit

**Pflichten**

* strikt valide `summary.json`
* deterministische Statusableitung
* keine implizite Heilung

**Striktheit**

* hoch
  Fehler sind Signale.

---

### wgx — *Boundary-Produzent & Dispatcher*

**Rolle**

* Veröffentlichung
* CLI-Interface
* Event-Emission

**Pflichten**

* kanonische Release-URL
* korrektes Artefakt

**Erlaubt**

* Fallbacks
* Warnungen statt Abbruch

wgx darf **nicht blockieren**.

---

### plexer — *Nicht-kritischer Transport*

**Rolle**

* Event-Weiterleitung

**Spezialregel**
`integrity.summary.published.v1` ist **BEST-EFFORT**

**Konsequenz**

* Fehler → `warn`
* keine Eskalation
* kein Retry-Zwang

Transport darf versagen, ohne Wahrheit zu beschädigen.

---

### chronik — *Pull-Orchestrator & Wahrheitswächter*

**Rolle**

* Einsammeln
* Vergleichen
* Bewahren

**Invarianten**

1. Ältere Daten überschreiben niemals neuere
2. Sanitization nur mit Spur

   * `generated_at_sanitized: true`
3. Netzwerkfehler überschreiben keine Wahrheit
4. Keine stille Heilung

---

### leitstand — *Strenger Beobachter*

**Rolle**

* Visualisierung
* Diagnose

**Prinzipien**

* niemals implizit OK
* fehlende Daten bleiben fehlend
* Ursachen sichtbar

Leitstand beruhigt nicht.

---

## 5. Artefakt vs. Event (harte Trennung)

| Dimension           | Artefakt | Event |
| ------------------- | -------- | ----- |
| Wahrheit            | ja       | nein  |
| Verlust tolerierbar | nein     | ja    |
| Transportabhängig   | nein     | ja    |
| Trigger             | nein     | ja    |

Jede Vermischung ist ein Architekturfehler.

---

## 6. Striktheitsmatrix

| Komponente | IO      | Semantik |
| ---------- | ------- | -------- |
| semantAH   | hoch    | hoch     |
| wgx        | mittel  | hoch     |
| plexer     | niedrig | niedrig  |
| chronik    | mittel  | hoch     |
| leitstand  | niedrig | hoch     |

Unterschiedliche Striktheit ist **Arbeitsteilung**, kein Widerspruch.

---

## 7. Verbotene Fehlannahmen

❌ „Wenn kein Event kam, ist alles gut.“
❌ „WARN kann man ignorieren.“
❌ „Chronik heilt Daten.“
❌ „Leitstand verschönert.“

---

## 8. Designziel

Integrität ist **kein Zustand**, sondern **permanenter Zweifel**.

> Die Integritätsneurose ist kein Bug,
> sondern das Immunsystem gegen Selbsttäuschung.

---

## 9. Bewusste Spannungen

* Zeitverzug zwischen Artefakt und Anzeige
* Menschliche Fehlinterpretation von WARN/MISSING

Diese Spannungen sind **akzeptiert**.

---

## 10. Schluss

Dieses System ist kein Kontrollsystem,
sondern ein **Misstrauenssystem mit Gedächtnis**.
