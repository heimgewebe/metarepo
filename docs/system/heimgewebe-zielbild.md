# Heimgewebe – Zielbild des Organismus

Dieses Dokument beschreibt das angestrebte Zielbild des Heimgewebe-Organismus.
Es verzichtet bewusst auf Ist-Zustand und Umsetzungstand und formuliert nur,
wie der Organismus gedacht ist, wenn die Architektur vollständig ausgebaut ist.

> **Klarstellung (Epistemische Rollen):**
> *   **Chronik ist passiv:** Sie speichert Events (Fakten), agiert aber nicht selbstständig.
> *   **Lernen ist nicht aktiv:** Heimlern beobachtet und generiert Feedback/Modelle, greift aber nicht aktiv in den operativen Fluss ein.

---

## 1. Leitprinzipien

1. Heimgewebe ist ein verteiltes System aus spezialisierten Repositories,
   das als zusammenhängender Organismus agiert.
2. Sprache und Struktur werden durch zentrale Contracts beschrieben,
   nicht durch implizite Absprachen im Code.
3. Wichtige Zustände werden als Events sichtbar gemacht, nicht als
   stille Seiteneffekte.
4. Semantische Bedeutung entsteht in einer zentralen Wissensschicht
   und wird von dort aus allen Komponenten bereitgestellt.
5. Motorik (Checks, Flows, Fleet-Aktionen) wird über einen
   einheitlichen Fleet-Motor gesteuert.
6. Meta-Reflexion und Lernen sind eigene Schichten, keine
   „Nebenprodukte“ einzelner Repos.

---

## 2. Achsen des Organismus

### 2.1 Achse A – Code & Contracts

- Interne Organismus-Contracts (z. B. `event.line`, `insights.daily`,
  `fleet.health`, `os.context.*`) sind im Metarepo definiert und
  werden von allen Fleet-Repos eingehalten.
- Externe API-Contracts (z. B. `aussen/v1`, `heimlern/v1`) sind im
  `contracts-mirror`-Repo definiert (Protobuf + JSON-Mirror) und bilden
  die offizielle Sprache nach außen.
- Alle relevanten Rust-Crates, Python-Module und Skripte beziehen
  sich explizit auf diese Contracts („Contracts first“).

### 2.2 Achse B – Events (Fakten)

- Chronik ist der zentrale append-only Event-Store für alle Domänen.
- Alle bedeutenden Zustandsänderungen im Organismus erzeugen Events
  nach dem gemeinsamen Schema `event.line`.
- Events beschreiben ausschließlich Fakten („ist passiert“), nicht
  Intentionen.
- Agenten und Dienste lesen primär aus Chronik, um Verlauf und
  Historie nachzuvollziehen und zu analysieren.

### 2.3 Achse C – Commands (Intentionen)

- Commands entstehen in klar getrennten Kanälen (z. B. GitHub-PR-Kommentare,
  UI-Aktionen im Leitstand, explizite Steueraufrufe).
- Commands werden standardisiert in ein gemeinsames Command-Schema
  (z. B. `heimgewebe.command.v1`) überführt und auditierbar gehalten.
- Commands sind Intentionsobjekte („bitte tue X“) und klar getrennt
  von Events („X wurde getan“).
- Alle wichtigen Commands sind replay-fähig (z. B. über Chronik und
  entsprechende Tools).

### 2.4 Achse D – WGX als Motorik

- WGX ist der zentrale Fleet-Motor:
  - führt Standard-Kommandos wie `guard`, `smoke`, `metrics`,
    `semantah` aus,
  - abstrahiert CI- und Local-Workflows über Fleet-Profile.
- Jedes Fleet-Repo besitzt ein `.wgx/profile.yml`, das seine
  Standardbefehle beschreibt.
- Fleet-Health und Metriken werden über WGX-Snapshots erzeugt
  (z. B. `fleet.health`, `metrics.snapshot`) und im Leitstand
  sichtbar gemacht.

### 2.5 Achse E – Wissens- und Semantikschicht

- SemantAH ist das zentrale Wissens- und Insight-System:
  - baut rekonstruktionsfähige Indizes und Graphstrukturen,
  - erzeugt `insights.daily` und weitere semantische Exporte.
- Semantische Verdichtung (Themen, Muster, Embeddings) findet
  primär hier statt, nicht verteilt über Einzelrepos.
- HausKI, Heimgeist, Leitstand und weitere Agenten beziehen ihre
  semantischen Sichten aus SemantAH.

### 2.6 Achse F – OS-Kontext

- Mitschreiber sammelt OS-, App- und Fensterkontext in einem WAL
  und generiert daraus `os.context.*` Events.
- OS-Kontext ist eine reguläre Achse des Organismus, nicht bloß
  ein lokales Hilfsfeature.
- SemantAH und HausKI nutzen OS-Kontext, um Arbeitssituationen
  und Entscheidungsumgebungen zu rekonstruieren.

---

## 3. Rollen der Repositories (Zielbild)

### 3.1 Metarepo – Struktur, Contracts, Policies

- Definiert interne Organismus-Contracts und hält sie konsistent.
- Enthält zentrale Architektur-Dokumente, Repo-Matrizen und
  Runbooks für den Organismus.
- Stellt WGX-Templates und Reusable Workflows bereit, an denen
  sich alle Fleet-Repos orientieren.
- Dient als Quelle der Wahrheit für Fleet-Definition, Profile
  und Cross-Repo-Policies.

### 3.2 Contracts – externe API-Schnittstellen

- Beschreibt alle externen API-Contracts (z. B. `aussen/v1`,
  `heimlern/v1`) in Protobuf und JSON-Mirror.
- Trägt die offizielle Sprache zwischen Heimgewebe und Außenwelt.
- Trennt externe Schnittstellen klar von internen Organismus-Contracts.

### 3.3 WGX – Fleet-Motorik & Metrikschicht

- Stellt eine einheitliche CLI und Standard-Workflows für alle
  Fleet-Repos bereit.
- Erzeugt Fleet-Metriken (`fleet.health`, `metrics.snapshot`)
  und weitere Auswertungen.
- Bindet SemantAH und Leitstand an, um Fleet-Verhalten sichtbar
  und steuerbar zu machen.

### 3.4 Chronik – Event-Store

- Hält alle Events des Organismus als append-only Log.
- Bildet die Grundlage für Auditing, Replays und zeitbasierte
  Analysen.
- Dient als gemeinsame Vergangenheitsachse für HausKI, Heimlern,
  SemantAH, Heimgeist und Leitstand.

### 3.5 Aussensensor – Außenwelt-Ingest

- Nimmt definierte externe Feeds und Signale auf.
- Wandelt sie in strukturierte `aussen.event.*`-Events und schreibt
  sie nach Chronik.
- Ist die bevorzugte Quelle für Außeninformationen; andere Repos
  greifen auf Außenwelt-Daten über Aussensensor/Chronik zu.

### 3.6 SemantAH – Wissens- und Insight-Schicht

- Konsolidiert Vault, Events, OS-Kontext und weitere Quellen in
  einem semantischen Graphen.
- Stellt `insights.daily` und weitere Exporte bereit, die von
  HausKI, Heimgeist und Leitstand genutzt werden.
- Bietet eine Query-API für semantische Fragen und Analysen.

### 3.7 HausKI – Entscheidungs- und Orchestrierungskern

- Kombiniert Events, Insights, Metriken und Kontext zu
  Entscheidungen und Aktionen.
- Orchestriert spezialisierte Agenten (z. B. Audio, Code-Analyse,
  Research) über definierte Schnittstellen.
- Gibt Entscheidungen transparent, reproduzierbar und
  kontraktbasiert in den Organismus zurück (Events, Erklärungen).

### 3.8 HausKI-Audio – Audio-Event-Schicht

- Setzt Audio-bezogene Entscheidungen von HausKI um.
- Erzeugt Audio-Events (`audio.event.*`), die in Chronik
  nachvollziehbar sind.
- Kapselt Audio-spezifische Logik, sodass HausKI Audio als
  klar definierte Fähigkeit adressiert.

### 3.9 Heimlern – Mustererkennung & Policy-Adaption

- Analysiert Events und Insights auf wiederkehrende Muster
  (Fehler, Erfolge, Drifts).
- Leitet daraus Policies, Constraints und Empfehlungen ab.
- Gibt Muster und Feedback wieder als Events/Strukturen in
  den Organismus zurück, die HausKI und Heimgeist nutzen.

### 3.10 Leitstand – UI & Visualisierung

- Stellt den Zustand des Organismus visualisiert dar:
  Events, Insights, Fleet-Health, Alarme, Trends.
- Dient als gemeinsame Oberfläche für Menschen und
  perspektivisch auch für Agenten.
- Bekommt seine Daten aus Chronik, SemantAH, WGX und
  weiteren definierten Feeds.

### 3.11 Heimgeist – Meta-Agent & Systemreflexion

- Beobachtet das Gesamtsystem, bewertet Risiken, Drifts,
  Prioritäten und Blindspots.
- Koordiniert Agenten-Aktivitäten, kann Playbooks und
  WGX-Flows anstoßen.
- Versteht Insights, Events, Fleet-Zustände und Kontext in
  ihrem Zusammenspiel.
- Erzeugt Insight-Events (`heimgeist.insight.v1`) für Chronik,
  um Analysen historisierbar zu machen.

### 3.12 Sichter – Review- & Analyse-Agent

- Führt Code- und Repo-Analysen aus (z. B. im Rahmen von PRs
  und CI).
- Gibt Ergebnisse als maschinenlesbares Feedback, Events,
  Metriken und Kommentare zurück.
- Arbeitet eng mit Heimgeist, HausKI und SemantAH zusammen,
  um technische Qualität und Kohärenz zu sichern.

### 3.13 Mitschreiber – OS-Kontext & Intent-Sampler

- Erfasst Arbeits- und Nutzungskontext (Fenster, Apps, Texte)
  lokal in einem WAL.
- Generiert `os.context.*`-Events, die SemantAH, HausKI und
  Heimgeist zur Verfügung stehen.
- Dient als zentrale Quelle für OS-/Nutzungs-Kontext im
  Organismus.

### 3.14 Plexer – Event-Router zwischen Agenten

- Leitet Events zwischen Agenten und Diensten weiter, mit
  Filterung, Priorisierung und Fan-out/Fan-in.
- Transportiert bewusst Fakten-Events, keine Commands.
- Entkoppelt Agenten voneinander, ohne zusätzliche
  Semantik-Schichten aufzuzwingen.

### 3.15 Tools – Hilfssystem für KI-Sichtbarkeit

- Generiert Merger, Snapshots und weitere Artefakte, die den
  Repos einen KI-freundlichen Überblick geben.
- Bietet verschiedene Detailgrade (z. B. dev, max) und
  Filter (Dateitypen, Ordnerarten).
- Spiegelt Repos, ohne eigene Wahrheiten zu definieren.

### 3.16 Weltgewebe & Vault-Gewebe – angrenzende Systeme

- Weltgewebe bildet öffentliche Web-/Dokumentationsoberflächen,
  steht neben der Fleet, aber nicht in ihr.
- Vault-Gewebe ist ein privater Obsidian-Vault, dient als
  Inhaltsquelle für SemantAH und ist als Mitglied mit Sonderstatus
  (privat, kein WGX-Profil) Teil des Organismus.

### 3.17 Webmaschine – Lokaler Anker

- Dient als lokaler Anker und Orientierungssystem für den Organismus.
- Stellt Tooling bereit, um Navigation und Verständnis zu unterstützen,
  und ergänzt die Tools-Schicht.

---

## 4. Querregeln des Zielbildes

1. Contracts werden zuerst definiert, dann implementiert.
2. Relevante Zustände erzeugen Events; nichts Wichtiges bleibt
   unsichtbar.
3. Semantik und Insights werden zentral in SemantAH erzeugt
   und wiederverwendet.
4. Fleet-Standardabläufe laufen über WGX-Profile.
5. Sichtbarkeit und Zustandssichten laufen über Leitstand.
6. Meta-Reflexion (Heimgeist) und Policy-Lernen (Heimlern)
   sichern Anpassungsfähigkeit und Kohärenz.

---

## 5. Essenz

Im Zielbild ist Heimgewebe ein Organismus aus klar benannten Achsen
und Rollen:

- Metarepo und Contracts definieren die Sprache.
- Chronik hält die Fakten.
- SemantAH erzeugt Bedeutung.
- HausKI entscheidet und orchestriert.
- Heimlern und Heimgeist justieren Verhalten und Prioritäten.
- WGX bewegt die Fleet.
- Leitstand zeigt, was los ist.
- Aussensensor und Mitschreiber liefern Außen- und OS-Kontext.
- Plexer verbindet Agenten, Tools machen alles für Menschen
  und KI zugänglich.

Die Stärke des Systems entsteht nicht aus einer einzelnen
Komponente, sondern aus dem Zusammenspiel dieser Linien.

---

## 6. Repo×Achsen-Matrix (Zielbild)

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
| heimgeist      | C                   | P/C                 | I                        | I                | C         | Meta-Agent, konsumiert Events/Kontext, produziert Insights                |
| sichter        | C                   | P/I                 | C/P (PR-Kommandos)       | I                | –         | Review-Agent, getriggert über CI/PR; kann Events/Metriken erzeugen        |
| mitschreiber   | C                   | P (os.context.*)    | –                        | –                | Kern      | OS-/App-/Fenster-Kontext → WAL → os.context-Events                        |
| plexer         | C                   | P/C (Routing)       | –                        | I                | –         | Event-Router zwischen Agenten, Faktenstrom                                |
| tools          | C                   | P/I                 | –                        | I                | –         | Merger/Snapshots; erzeugen Artefakte, teils Event- oder Metrik-Ausgaben   |
| webmaschine    | C                   | –                   | –                        | I                | –         | Lokaler Anker, Tooling                                                    |
| weltgewebe     | –                   | –                   | –                        | –                | –         | Nachbarsystem (Web/Doku), nicht Fleet                                     |
| vault-gewebe   | –                   | –                   | –                        | –                | –         | Privater Vault, Quelle für semantAH (Sonderstatus: privat)               |
```

---
