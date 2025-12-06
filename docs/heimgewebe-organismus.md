# Heimgewebe als Organismus

Dieses Dokument beschreibt Heimgewebe als technischen Organismus:

- welche Repos welche „Organe“ darstellen,
- welche Muster dort gut gelöst sind,
- was andere Repos davon explizit übernehmen sollen.

Ziel: Cross-Pollination sichtbar machen, statt jedes Repo isoliert zu betrachten.

---

## 1. Organismus-Übersicht

Kernachsen:

- **Control-Plane:** `metarepo`, `contracts`, `wgx`
- **Gedächtnis & Sinn:** `chronik`, `semantAH`, `vault-gewebe`
- **Entscheidung:** `hausKI`, `heimlern`
- **Peripherie & UI:** `aussensensor`, `leitstand`, `tools`, Satelliten (z. B. `sichter`, `mitschreiber`)

Merksatz:

> Code lebt in vielen Repos, aber **der Organismus** ist eins.

---

## 2. Muster pro Repo – und was die anderen davon lernen sollen

### 2.1 metarepo – Contracts, CI, ADRs

**Leitmuster:**
- JSON-Schemas unter `contracts/*.schema.json` als zentrale Verträge.
- Reusable Workflows für Fleet-weit einheitliche Checks.
- ADRs als explizite Architekturentscheidungen.

**Empfohlene Übernahmen für alle Repos:**
- Sich auf Contracts im metarepo beziehen (statt eigene Schemas zu erfinden).
- Für neue Formate zuerst Contract im metarepo definieren.
- Änderungen an Datenstrukturen immer mit ADR oder kurzem Decision-Log verknüpfen.

---

### 2.2 contracts – gemeinsame Sprache

**Leitmuster:**
- Kanonische Schemas für z. B.:
  - `event.line`
  - `fleet.health`
  - `insights.daily`
- Fokus auf minimale, aber stabile Strukturen.

**Empfohlene Übernahmen:**
- `chronik` schreibt Events strikt im Format `event.line`.
- `semantAH` produziert `insights.daily` exakt nach Contract.
- `leitstand` konsumiert `fleet.health` und `insights.daily` ausschließlich über die Contracts.
- Neue Repos definieren lieber kleine Sub-Contracts als freies JSON.

---

### 2.3 wgx – Fleet-CLI und Profile

**Leitmuster:**
- `.wgx/profile.yml` als deklaratives Profil pro Repo.
- Einheitliche Kommandos (`wgx guard`, `wgx smoke`, `wgx metrics`).
- Klare Trennung:
  - „Was will das Repo?“ → Profile
  - „Wie wird es ausgeführt?“ → wgx-Implementierung.

**Empfohlene Übernahmen:**
- Jedes Fleet-Repo besitzt ein `.wgx/profile.yml`.
- CI-Workflows rufen wgx-Kommandos auf, statt eigene Shell-Orgien zu bauen.
- Repos beschreiben ihr Selbstbild (Wichtigkeit, Checks, Metriken) im Profile statt in zig YAML-Varianten.

---

### 2.4 chronik – Event-Gedächtnis

**Leitmuster:**
- Append-only Event-Store (JSONL) mit klaren Pfaden.
- Trennung von:
  - Ingest (schreibende Systeme)
  - Query/Lesen (auswertende Systeme).

**Empfohlene Übernahmen:**
- Alle Repos, die „etwas Wichtiges“ tun, können optional Events in `chronik` schreiben.
- Statt Logs nur in CI-Logs zu verlieren → wichtige Zustandswechsel als `event.line` in `chronik`.
- hausKI-Entscheidungen, Lern-Updates aus `heimlern` und WGX-Metriken sollten Events hinterlassen.

---

### 2.5 semantAH – Sinnschicht und Insights

**Leitmuster:**
- Rebuildbare Indizes unter `.gewebe/index/*`.
- Tägliche Insights unter `.gewebe/insights/daily/` + `today.json`.
- Strenge Trennung:
  - Quelle: Vault-Dateien
  - Ableitung: Embeddings, Topics, Fragen.

**Empfohlene Übernahmen:**
- Andere Repos dürfen Annahmen über Insights **nur** machen, wenn sie dem Contract `insights.daily` folgen.
- hausKI nutzt Insights für Entscheidungen, anstatt selbst wild durch den Vault zu parsen.
- leitstand verwendet semantAH als einzige Wahrheit für „Top-Themen des Tages“.

---

### 2.6 hausKI – Entscheider mit Gedächtnis

**Leitmuster:**
- Zentrale Entscheidungslogik (Playbooks, Policies).
- Konsum von:
  - Events aus `chronik`
  - Insights aus `semantAH`
  - Health aus `fleet.health`.
- Rückschreiben der eigenen Entscheidungen als Events.

**Empfohlene Übernahmen:**
- hausKI sollte **immer** über `chronik` und Contracts arbeiten, nicht über direkte Datei-Hacks.
- Andere Repos delegieren komplexere „Was soll ich tun?“-Fragen an hausKI, statt überall Mikro-Logik einzubauen.

---

### 2.7 heimlern – Lernen aus Feedback

**Leitmuster:**
- Bandit-/Policy-Layer, der Regeln über Erfahrungen verbessert.
- Nutzt chronik-Events und explizites Feedback.

**Empfohlene Übernahmen:**
- hausKI und WGX verwenden heimlern als „Meta-Schicht“, wenn es um:
  - Priorisierung
  - Eskalationen
  - Wiederholte Fehler geht.
- Repos, die Entscheidungen treffen, loggen Feedback wieder als Events, damit heimlern lernen kann.

---

### 2.8 aussensensor – kontrollierte Außenwelt

**Leitmuster:**
- Kuratierter Zufluss von externen Feeds.
- Klare Grenze zwischen Außen und Innen.

**Empfohlene Übernahmen:**
- Keine Repo-übergreifenden Direktzugriffe auf externe Feeds – alles über aussensensor → chronik.
- semantAH und hausKI nutzen externe Informationen nur, wenn sie als Events/Docs durch aussensensor gelaufen sind.

---

### 2.9 leitstand – Dashboard und Taktgeber

**Leitmuster:**
- Täglicher Digest aus:
  - `fleet.health`
  - `insights.daily`
  - `event.line` (ausgewählte Events).
- Klarer Fokus auf:
  - Übersicht statt Detail
  - „Was braucht Aufmerksamkeit?“

**Empfohlene Übernahmen:**
- Neue Module, die „sichtbar“ sein wollen, liefern Daten in eines der existierenden Contracts, statt eigene Dashboards zu bauen.
- hausKI und heimlern können Leitstand-Daten als „What’s important today?“-Startpunkt nutzen.

---

### 2.10 tools – Werkzeuggürtel

**Leitmuster:**
- Merger, Generatoren, Helferskripte, die Repos für Menschen und KIs aufbereiten.

**Empfohlene Übernahmen:**
- Repos nutzen vorhandene Merger/Generatoren, statt eigene Ad-hoc-Skripte anzuhäufen.
- Wenn ein neues Tool generisch nützlich ist → nach `tools` ziehen.

---

## 3. Cross-Pollination-Regeln (Fleet-weit)

1. **Contracts first.**
   Neue Datenformate entstehen zuerst im `contracts`-Ordner des metarepo.

2. **Events statt stummer Seiteneffekte.**
   Wichtige Aktionen erzeugen `event.line` in `chronik`.

3. **WGX statt Einzel-Workflows.**
   CI und lokale Commands gehen über `wgx` und `.wgx/profile.yml`.

4. **semantAH statt Vault-Scraping.**
   Für Bedeutungsfragen sind Insights und Indexe zuständig, nicht ad-hoc-Suchen.

5. **Leitstand als gemeinsames Display.**
   Sichtbarkeit geht über leitstand, nicht über Repo-spezifische Dashboards.

6. **heimlern als Meta-Schicht.**
   Langfristige Anpassung (z. B. Priorisierung, Eskalation) wird über heimlern betrachtet.

---

## 4. Wie neue Repos sich einordnen sollen

Neue Repos beantworten früh:

1. Welche Contracts nutze ich? Welche brauche ich neu?
2. Welche Events schreibe ich nach chronik?
3. Welche WGX-Kommandos sind für mich verbindlich?
4. Welche Einsichten kann semantAH aus meinen Daten ziehen?
5. Was soll langfristig im Leitstand sichtbar sein?

Dieses Dokument ist der Referenzpunkt für diese Fragen.
