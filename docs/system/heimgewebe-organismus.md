# Heimgewebe – Organismusübersicht

Heimgewebe besteht aus spezialisierten Repositories, die zusammen einen verteilten, ereignis- und wissensbasierten Organismus bilden.
Jede Komponente ist mit einem der drei Labels markiert:

- **(IST)** heute im Code erkennbar
- **(ZIEL)** intendierte Weiterentwicklung
- **(POLICY)** verbindliche Architekturregel

---

## 0. Makrostruktur des Organismus

### 0.1 Parallele Achsen

- **Ereignisachse**
  (IST) Events aus Außenwelt, OS-Kontext, Fleet, Audio, CI werden erzeugt und in `chronik` persistiert.

- **Wissensachse**
  (IST) `semantAH` erzeugt rekonstruierbare Insights, Einbettungen, Graphstrukturen.

- **Entscheidungsachse**
  (IST) `hausKI` trifft Entscheidungen basierend auf Insights, Events und weiteren Kanälen.

- **Fleet-/Metrikachse**
  (IST) `wgx` erzeugt Metriken und Statuspunkte (`fleet.health`, `metrics.snapshot`).

- **OS-Kontextachse**
  (IST) `mitschreiber` sammelt Desktop-/App-Kontext in einem WAL und generiert daraus `os.context.*` Events.

(POLICY) Keine dieser Achsen ist „fundamental“. Das System entsteht aus ihrer Wechselwirkung.

---

## 1. Kommunikations- und Integrationsachsen

### 1.1 Achse A – Code & Contracts

- (IST) Interne JSON-Schemas für Organismus-Contracts
  (z. B. `event.line`, `insights.daily`, `fleet.health`) liegen im Metarepo
  unter `contracts/*.schema.json`.
- (IST) Externe API-Contracts (z. B. `aussen/v1`, `heimlern/v1`) liegen
  im `contracts-mirror`-Repo als Protobuf + JSON-Mirror.
- (IST) Rust-Crates, Python-Module und Skripte nutzen diese Contracts
  explizit (z. B. hausKI, heimlern, aussensensor).
- (POLICY) „Contracts first“: Neue Formate werden zuerst als Schema
  beschrieben, erst dann im Code verwendet.

### 1.2 Achse B – Events (Fakten)

- (IST) `chronik` führt einen append-only JSONL-Eventstore
  (`event.line`).
- (IST) Mehrere Repos schreiben Events, u. a. `aussensensor`, `heimlern`,
  hausKI-Entscheidungen und CI-/Fleet-Signale.
- (IST) `plexer` kann Events entgegennehmen und an Konsumenten
  wie `heimgeist` weiterreichen.
- (POLICY) Events beschreiben Fakten („ist passiert“), nicht Intentionen.
- (POLICY) Wichtige Zustandsänderungen sollten als Events sichtbar werden,
  statt als stiller Seiteneffekt zu verschwinden.

### 1.3 Achse C – Commands (Intentionen)

- (IST) Commands entstehen heute vor allem über GitHub-PR-Kommentare
  (z. B. `@heimgewebe/sichter /quick`). Diese werden geparst und in
  Eventform (z. B. `heimgewebe.command.v1`) überführt.
- (ZIEL) Commands sollen vollständig auditierbar und replay-fähig sein
  (z. B. über chronik und leitstand).
- (POLICY) Commands = Intentionen („bitte tue X“),
  Events = Fakten („X wurde getan“). Niemals mischen.

### 1.4 Achse D – WGX als Motorik

- (IST) Mehrere Repos sind WGX-fähig (`![WGX]`-Badge, `.wgx/profile.yml`,
  WGX-Skripte).
- (IST) WGX-Skripte erzeugen u. a. Fleet-Metriken, die von hausKI
  eingelesen werden.
- (ZIEL) Alle Fleet-Repos nutzen WGX für Standardabläufe
  (`guard`, `smoke`, `metrics`, `semantah`).
- (POLICY) Lieber einheitliche WGX-Kommandos als Repo-spezifische
  Shell-Inseln.

---

## 2. Repositories

---

## 2.1 metarepo – Struktur, Contracts, Policies

- (IST) Enthält übergeordnete Architektur-Dokumente und Cross-Repo-Richtlinien.
- (IST) Führt interne Organismus-Contracts (`event.*`, `insights.daily`, `fleet.health`, `os.context.*`).
- (IST) Enthält WGX-Vorlagen und Reusable Workflows.
- (ZIEL) Vollständige Fleet-Definition (Welche Repos? Welche Profile? Welche Policies?).
- (POLICY) Architekturänderungen beginnen hier.

**Kommunikation:** indirekt mit allen Repos via Contracts und Workflows.

---

## 2.2 contracts-mirror – externe API-Schnittstellen

- (IST) Beinhaltet formale API-Schemas für Außenweltkommunikation (`aussen/v1`, `heimlern/v1`, weitere Protobuf-Schnittstellen).
- (ZIEL) Alle externen Systeme sprechen ausschließlich über hier definierte Schnittstellen.
- (POLICY) Innen-Contracts = metarepo; externe API = contracts-mirror.

**Kommunikation:** außen nach innen; genutzt von hausKI, aussensensor, heimlern.

---

## 2.3 wgx – Fleet-Motorik & Metrikschicht

- (IST) WGX-CLI, Guard-/Smoke-Workflows, metrics-Tools, semantAH-Integrationen.
- (IST) Generiert `fleet.health` und `metrics.snapshot`.
- (ZIEL) Einheitliche Standard-Kommandos und gleiche CI-Mechanik für die gesamte Fleet.
- (POLICY) Neue Repos erhalten ein `.wgx/profile.yml`.

**Kommunikation:** liest/steuert die Fleet; liefert Metriken an leitstand, hausKI, heimgeist, chronik.

---

## 2.4 chronik – Event-Store

- (IST) Append-only Eventlog (`event.line`).
- (IST) Ingest aus aussensensor, hausKI, heimlern, heimgeist, CI, WGX, mitschreiber.
- (ZIEL) Vollständiges Replay, Querying, Langzeitarchiv.
- (POLICY) Zustandsrelevante Änderungen erzeugen Events statt stiller Seiteneffekte.

**Kommunikation:** zentrale Vergangenheitsachse.

---

## 2.5 aussensensor – Außenwelt-Ingest

- (IST) Liest definierte Feeds/Quellen und erzeugt `aussen.event.*`.
- (ZIEL) einzige standardisierte Außen-Ingest-Schicht.
- (POLICY) andere Repos holen Außeninformationen nicht direkt, sondern via aussensensor/chronik.

**Kommunikation:** Außenwelt → aussensensor → chronik → semantAH/hausKI/heimlern/heimgeist.

---

## 2.6 semantAH – Wissens-/Insight-Schicht

- (IST) Erzeugt `insights.daily`, Einbettungen, Graphstrukturen; konsolidiert Vault, Events, OS-Kontext.
- (IST) zentrales Wissenssubsystem: Rekonstruktion, Verdichtung, Bedeutung.
- (ZIEL) vollständiger semantischer Graph mit Query-API.
- (POLICY) semantische Verarbeitung erfolgt hier, nicht verteilt.

**Kommunikation:** konsumiert chronik, os.context.* und liefert Insights an hausKI, heimgeist, leitstand.

---

## 2.7 hausKI – Entscheidungs- und Orchestrierungskern

- (IST) Rust-basierter Entscheidungsagent, konsumiert Events, Insights, Metriken.
- (IST) zentrale Instanz zur Erzeugung von Handlungen, Reaktionen, Audio-Befehlen, Pattern-Analysen.
- (ZIEL) Multi-Agent-Orchestrator; Integrationszentrum für plexer, semantAH, heimlern, hausKI-audio.
- (POLICY) Entscheidungen sind beobachtbar, reproduzierbar, kontraktbasiert.

**Kommunikation:** semantAH ↔ hausKI ↔ heimlern ↔ heimgeist ↔ leitstand ↔ chronik.

---

## 2.8 hausKI-audio – Audio-Event-Schicht

- (IST) verarbeitet Audio-Kommandos von hausKI; erzeugt `audio.event.*`.
- (ZIEL) geschlossener Regelkreis: hausKI → audio → chronik → semantAH/heimgeist.
- (POLICY) Audio bleibt gekapselt und moduliert, kein Spezialpfad in anderen Repos.

**Kommunikation:** hausKI ↔ hausKI-audio ↔ chronik.

---

## 2.9 heimlern – Mustererkennung & Policy-Adaption

- (IST) Rust-Library, die wiederkehrende Muster in chronik/Insights erkennt.
- (IST) kann Patterns und Feedback zurück in den Organismus geben.
- (ZIEL) permanente Policy-Autoadaption; systemisches Lernen.
- (POLICY) Muster werden sichtbar gemacht (Events, Feedback), nicht still implementiert.

**Kommunikation:** chronik ↔ heimlern ↔ hausKI ↔ heimgeist.

---

## 2.10 leitstand – UI & Visualisierung

- (IST) Dashboard für Events, Insights, Fleet-Status.
- (IST) Oberflächensicht auf den Zustand des Organismus.
- (ZIEL) zentrale Sicht für Menschen und Agenten.
- (POLICY) keine parallelen Dashboards für Organismuszustand in anderen Repos.

**Kommunikation:** konsumiert semantAH, chronik, fleet.health.

---

## 2.11 heimgeist – Meta-Agent, Koordination & Systemreflexion

- (IST) Meta-Agent, der Events, Metriken, Insights beobachtet und bewertet.
- (IST) erkennt Drift, Fehlstellen, Prioritäten.
- (ZIEL) orchestriert Agenten-Aktivität, kann Playbooks auslösen, WGX-Checks modulieren.
- (POLICY) Meta-Reflexion liegt hier, nicht verteilt.

**Kommunikation:** semantAH ↔ heimgeist ↔ hausKI ↔ sichter ↔ leitstand.

---

## 2.12 sichter – Review-/Analyse-Agent

- (IST) PR-Analysen, Codebewertungen, Qualitätssicherung, ausgelöst via CI oder PR-Kommandos.
- (IST) generiert Kommentare, potenziell Events/Metriken.
- (ZIEL) tiefe Integration in Insights, heimgeist, hausKI.
- (POLICY) Ergebnisse sollen maschinenlesbar zurückfließen.

**Kommunikation:** GitHub ↔ sichter ↔ heimgeist/hausKI ↔ chronik.

---

## 2.13 mitschreiber – OS-Kontext & Intent-Sampler

- (IST) lokaler Prozess, der OS-/App-/Fensterkontext in einer WAL sammelt.
- (IST) erzeugt `os.context.*` Events (Text, Fenster, Apps, Embedding-Material).
- (ZIEL) OS-Kontext als vollwertige Achse für semantische Rekonstruktion.
- (POLICY) OS-Kontext wird ausschließlich über mitschreiber erhoben.

**Kommunikation:** OS → mitschreiber → chronik → semantAH → hausKI/heimgeist.

---

## 2.14 plexer – Event-Router zwischen Agenten

- (IST) minimaler HTTP-basierter Event-Router.
- (IST) leitet Fakten-Events an mehrere Konsumenten weiter.
- (ZIEL) Multi-Agent-Bus mit Filterung, Priorisierung, Fan-out/Fan-in.
- (POLICY) Faktenstrom = plexer; Intentionen = getrennte Kanäle.

**Kommunikation:** Agenten ↔ plexer ↔ weitere Agenten.

---

## 2.15 tools – Hilfssystem für KI-Sichtbarkeit

- (IST) enthält Merger, Extraktoren, Snapshot-Generatoren.
- (IST) erzeugt KI-freundliche, mehrstufige Repräsentationen der Repos.
- (ZIEL) vollständige, wählbare Detailstufen (dev, max) für den gesamten Fleet-Bestand.
- (POLICY) Tools erzeugen keine eigenen Wahrheiten; sie spiegeln die Repos.

**Kommunikation:** liest alle Repos → erzeugt Artefakte für KI/Agenten.

---

## 2.16 weltgewebe & vault-gewebe – angrenzende Systeme

- (IST) weltgewebe = Öffentlichkeits- und Dokumentationsoberfläche, Related/Satellite.
- (IST) vault-gewebe = privater Obsidian-Vault, dient als Inhaltseinspeisung für semantAH (Fleet).
- (POLICY) weltgewebe bleibt bewusst außerhalb der Fleet (Satellite), vault-gewebe wird integriert.

---

## 3. Querregeln

1. **Contracts first**
   Neue Formate werden zuerst als Contract beschrieben.

2. **Events statt Seiteneffekte**
   Zustandsveränderungen müssen sichtbar sein.

3. **Zentrale Semantik**
   Wissensbildung erfolgt in semantAH.

4. **WGX als Fleet-Standard**
   Einheitliche Kommandos, Profile, Checks.

5. **Leitstand-Sichtbarkeit**
   Relevante Systemdaten sollen sichtbar werden.

6. **Meta-Reflexion**
   heimgeist/heimlern bilden die Anpassungsschicht des Systems.

---

## 4. Essenz

Der Organismus besteht aus mehreren parallel arbeitenden Achsen.
Bedeutung entsteht in semantAH, Entscheidungen in hausKI, Reflexion in heimgeist, Kontext in mitschreiber, Sichtbarkeit in leitstand, Persistenz in chronik, Fleet-Steuerung in wgx.

Die Kraft des Systems entsteht aus ihrer Interaktion, nicht aus einer einzelnen Komponente.

---

## 5. Repo×Achsen-Matrix

**Legende**

- **P** = produziert
- **C** = konsumiert
- **P/C** = produziert und konsumiert
- **T** = Templates / Definition, kein Laufzeit-Flow
- **I** = indirekt (über andere Komponenten)
- **–** = keine nennenswerte Rolle auf dieser Achse

```markdown
| Repo           | A: Code & Contracts | B: Events (Fakten) | C: Commands (Intention) | D: WGX (Motorik) | OS-Kontext | Kommentar                                                                 |
|----------------|---------------------|---------------------|--------------------------|------------------|-----------|---------------------------------------------------------------------------|
| metarepo       | T                   | T                   | T                        | T                | –         | Definiert interne Contracts, Policies, WGX-Templates                      |
| contracts-mirror| T                   | –                   | –                        | –                | –         | Definiert externe API-Schemas (aussen/v1, heimlern/v1, …)                |
| wgx            | C                   | P/C (Metrik-Events) | P (indirekt)             | Kern             | –         | Steuert Fleet-Kommandos, erzeugt Metriken/Fleet-Health                    |
| chronik        | C                   | P/C                 | I                        | I                | C         | Zentraler Event-Store, nimmt viele Linien auf                             |
| aussensensor   | C                   | P                   | –                        | I                | –         | Wandelt externe Feeds in aussen.event.* und schreibt nach chronik        |
| semantAH       | C                   | C                   | I                        | I                | C         | Baut Insights/Graph aus Events, Vault, OS-Kontext                         |
| hausKI         | C                   | C                   | P/C                      | C                | C         | Orchestrator, liest alles Relevante, erzeugt Entscheidungen/Events        |
| hausKI-audio   | C                   | P                   | I                        | I                | –         | Audio-spezifische Events und Steuerung                                    |
| heimlern       | C                   | C                   | I                        | I                | C         | Muster-/Policy-Schicht auf Events, Insights und Kontext                   |
| leitstand      | C                   | C                   | I                        | I                | I         | Visualisiert Events, Insights, Fleet-Health                               |
| heimgeist      | C                   | C                   | I                        | I                | C         | Meta-Agent, konsumiert v. a. Events, Insights, Kontext                    |
| sichter        | C                   | P/I                 | C/P (PR-Kommandos)       | I                | –         | Review-Agent, getriggert über CI/PR; kann Events/Metriken erzeugen        |
| mitschreiber   | C                   | P (os.context.*)    | –                        | –                | Kern      | OS-/App-/Fenster-Kontext → WAL → os.context-Events                        |
| plexer         | C                   | P/C (Routing)       | –                        | I                | –         | Event-Router zwischen Agenten, Faktenstrom                                |
| tools          | C                   | P/I                 | –                        | I                | –         | Merger/Snapshots; erzeugen Artefakte, teils Event- oder Metrik-Ausgaben   |
| heim-pc    | T                   | –                   | –                        | –                | –         | Lokaler Anker, Tooling                                                   |
| vault-gewebe   | –                   | –                   | –                        | –                | –         | Privater Vault, Quelle für semantAH (Fleet-Mitglied)                     |
| weltgewebe     | –                   | –                   | –                        | –                | –         | Nachbarsystem (Web/Doku), nicht Fleet                                     |
```

**Mini-Erläuterungen pro Achse**

- **Achse A – Code & Contracts**
  Starke Knoten: `metarepo`, `contracts-mirror`, `hausKI`, `heimlern`, `aussensensor`, `semantAH`, `wgx`.
  Sprach- und Strukturmacht liegt beim Metarepo (innen) und beim Contracts-Mirror-Repo (außen).

- **Achse B – Events (Fakten)**
  Stark produzierend: `aussensensor`, `hausKI-audio`, `mitschreiber`, `wgx`, `sichter`, `heimgeist` (perspektivisch).
  Stark konsumierend: `chronik`, `semantAH`, `heimlern`, `hausKI`, `leitstand`, `heimgeist`.

- **Achse C – Commands (Intentionen)**
  Ursprung: vor allem GitHub (PR-Kommentare), hausKI-Tools und CI.
  Primär betroffen: `sichter`, `hausKI`, `wgx`, perspektivisch stärker `heimlern`/`heimgeist`.
  Wichtig: `plexer` bleibt explizit *nicht* Command-Bus.

- **Achse D – WGX (Motorik)**
  Zentrum: `wgx`.
  WGX-fähig: alle Fleet-Repos mittelfristig; heute schon einige.
  Sichtbar über: `fleet.health`, Metrik-Events, leitstand-Panels.

- **OS-Kontext**
  Zentrum: `mitschreiber`.
  Nutznießer: `semantAH`, `heimlern`, `hausKI`, `heimgeist`.
  `chronik` spielt als Sekundärspeicher mit, aber nicht als Initiator.
