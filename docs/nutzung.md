# Heimgewebe – Nutzung & täglicher Betrieb

Heimgewebe ist ein verteiltes System aus mehreren Repos, das zusammen wie ein
autopoetischer KI-Organismus funktioniert:

- **metarepo** – Control-Plane (Contracts, CI-Vorlagen, Fleet-Definition)
- **wgx** – Werkzeugkasten und Fleet-Motorik
- **hausKI** – KI-Orchestrator mit Gedächtnis
- **semantAH** – semantischer Index und Insights
- **chronik** – Ereignisspeicher (Event-Log, Audit)
- **leitstand** – UI / Dashboard
- plus weitere Organe: **aussensensor**, **heimlern**, **vault-gewebe**, **weltgewebe**, **tools**, **sichter**, **mitschreiber**, **heimgeist**, **plexer**.

Dieses Dokument erklärt:

1. Wie du Heimgewebe im Alltag benutzt.
2. Welche Features es gibt.
3. Wo die jeweiligen Repos und Dokumente zu finden sind.

---

## 1. Schnellstart – „Wie bediene ich das Ding?“

### 1.1 Mindset

Heimgewebe ist **kein Monorepo**, sondern eine Fleet mit klaren Rollen.
Die Grundidee:

> *metarepo definiert, was richtig ist – wgx sorgt dafür, dass die Repos sich daran halten.*

Contracts im metarepo legen fest, wie Events, Insights, Metrics aussehen sollen;
Repos wie hausKI, semantAH, chronik, aussensensor usw. sind Producer/Consumer
dieser Datenströme.

### 1.2 Typischer Tagesablauf (Operator-Sicht)

Ganz grob:

1. **Fleet-Status prüfen**
   - GitHub Actions → `wgx-metrics` und CI-Workflows beobachten.
   - Optional: Metrics-Snapshots an eine Ingest-URL posten (chronik/leitstand).

2. **Wissenslage checken**
   - `semantAH` erzeugt tägliche Vault-Insights nach
     `contracts/insights.daily.schema.json`.
   - hausKI / Leitstand können `topics`, `questions`, `deltas` daraus visualisieren.

3. **Events & Incidents ansehen**
   - `chronik` speichert hausKI-Events im Format `event.line.schema.json`.
   - Leitstand liest daraus Dashboards und Tages-Digests.

4. **Arbeit an Repos**
   - WGX-Befehle nutzen (`wgx guard`, `wgx metrics snapshot` etc.).
   - sichter/mitschreiber/heimgeist als Reflexions- und Schreib-Hilfen dazunehmen.

Kurzfassung für Dummies:
> Heimgewebe ist ein Haufen Repos, die so tun, als wären sie ein Körper.
> metarepo ist das Regelbuch, wgx die Muskeln, hausKI das Gehirn,
> semantAH das Bedeutungs-Gedächtnis und chronik das Tagebuch.

---

### 1.3 Alle Repos lokal klonen

Nutze das Helper-Skript, um die komplette Fleet aus `repos.yml` auf einmal zu
holen (inklusive Owner-Fallback aus `github.owner`):

```bash
python scripts/clone_repos.py --dest heimgewebe-repos
```

- Optional: `--owner <ORG>` überschreibt den GitHub-Owner aus der Config.
- Optional: `--update` aktualisiert bestehende Clones per `git fetch`/`git pull`.
- Subset klonen: Repository-Namen als Argumente anhängen, z. B.
  `python scripts/clone_repos.py hausKI semantAH`.


## 2. Feature-Übersicht nach Repo (mit Links)

> Hinweis: Die GitHub-Links nehmen `heimgewebe` als Organisation an.

### 2.1 Control-Plane (metarepo)

**Repo:** `heimgewebe/metarepo`

- **Repo-Matrix & Fleet-Übersicht**
  - Welche Repos es gibt, ihre Rolle (z. B. memorativ, semantisch, politisch) und ihr Reifegrad.
  - Nutze sie als Einstieg, um zu verstehen, welches Repo wofür zuständig ist.

- **Contracts (Schemas)**
  - `contracts/event.line.schema.json` – hausKI → chronik Event-Schema.
  - `contracts/insights.daily.schema.json` – semantAH Daily-Insights, Consumer: hausKI, chronik.
  - `contracts/insights.schema.json` – Review-Insights (z. B. aus semantAH/sichter).
  - `contracts/dev.tooling.schema.json` – wie Repos ihre Tooling-Umgebung beschreiben (Language, Tests, LSP etc.).

- **Reusable CI-Workflows**
  - `.github/workflows/wgx-metrics.yml` – Fleet-weiter Metrics-Snapshot.
  - Weitere Reusables (Guard/Smoke etc.) sind ähnlich aufgebaut und ziehen Schemas per Tag `contracts-v1` aus metarepo.

**Nutzen:**
metarepo ist die **einzige** Quelle der Wahrheit für Contracts und gemeinsame CI-Bausteine.
Alle anderen Repos sollten auf diese Dateien verlinken, nicht eigene Varianten pflegen.

---

### 2.2 wgx – Fleet-Motorik

**Repo:** `heimgewebe/wgx`

- CLI und Scripte für:
  - `wgx metrics snapshot` – erzeugt Metrics-Payloads, die gegen `metrics.snapshot.schema.json` validiert werden.
  - Guard/Smoke-Runs für Repos.
- Wird in CI über `.github/workflows/wgx-metrics.yml` und andere Reusables aufgerufen.

**Nutzen:**
wgx macht aus „Organismus“ einen **beweglichen** Organismus: einheitliche Befehle,
die lokal und in CI gleich funktionieren.

---

### 2.3 hausKI – KI-Orchestrator

**Repo:** `heimgewebe/hausKI`

- Schreibt Events nach `chronik` im Format `contracts/event.line.schema.json`.
- Nutzt semantAH-Insights (`insights.schema.json`, `insights.daily.schema.json`) als Kontext.
- Dreht Entscheidungen und Playbooks für andere Repos.

**Nutzen:**
hausKI ist das **entscheidende Gehirn**: es verknüpft Metriken, Events, semantische
Insights und Policies zu Aktionen.

---

### 2.4 semantAH – semantischer Index & Insights

**Repo:** `heimgewebe/semantAH`

- Producer für:
  - `insights.daily` – Tages-Zusammenfassung des Wissenszustands, Schema siehe Contracts.
  - `insights` – Review-Insights (z. B. aus Code-Analyse).
- Arbeitet gegen den Vault (`vault-gewebe`) und andere Quellen.

**Nutzen:**
semantAH beantwortet die Frage: **„Was ist gerade wichtig?“**
hausKI/Leitstand müssen dann nur noch entscheiden, wie sie darauf reagieren.

---

### 2.5 chronik – Ereignisspeicher

**Repo:** `heimgewebe/chronik`

- Speichert hausKI-Events im JSONL-Format gemäß `event.line.schema.json`.
- Ist Consumer von:
  - `insights.daily` (Tages-Zusammenfassungen)
  - `insights` (Review-Insights)
- Dient als Audit-Log und Basis für Leitstand-Dashboards.

**Nutzen:**
chronik ist das **Langzeit-Gedächtnis**.
Ohne chronik wüsste niemand mehr, was gestern schiefgelaufen ist – außer deinem Gefühl,
und das ist notoriously nicht CI-kompatibel.

---

### 2.6 leitstand – Dashboard & Digests

**Repo:** `heimgewebe/leitstand`

- UI-Schicht für:
  - Fleet-Health (wgx-Metrics, CI-Status)
  - Tages-Digest aus `insights.daily`
  - Event-Ansichten aus `chronik`
- Arbeitet nur über dokumentierte Gateways (kein Direktzugriff auf rohe Files).

**Nutzen:**
leitstand ist das **Gesicht** des Heimgewebes – der Ort, an dem die
ganzen JSONs zu einem Bild werden.

---

### 2.7 aussensensor – kuratierte Außenwelt

**Repo:** `heimgewebe/aussensensor`

- Holt kuratierte Feeds (z. B. Nachrichten, Telemetrie, externe APIs).
- Transformiert sie in Events nach metarepo-Contracts und schreibt sie in chronik.
- Achtet auf Sicherheitsgrenzen: keine direkten Agent-Prompts von außen,
nur strukturierte Events.

**Nutzen:**
aussensensor sorgt dafür, dass der Organismus etwas von der Außenwelt mitbekommt,
ohne dass jeder RSS-Feed direkt am Hirnstamm zieht.

---

### 2.8 heimlern – Policies & Bandit-Logik

**Repo:** `heimgewebe/heimlern`

- Setzt Policy- und Bandit-Entscheidungen für hausKI und Co. um.
- Nutzt Events/Insights aus chronik/semantAH als Feedback.
- Ziel: aus wiederkehrenden Mustern bessere Entscheidungen machen.

**Nutzen:**
heimlern ist die **Politik** des Systems: es beschließt, welche Strategien
langfristig „gewählt“ bleiben.

---

### 2.9 vault-gewebe – Vault / Notizen

**Repo:** `heimgewebe/vault-gewebe`

- Enthält Obsidian-Vault mit Notizen, ADR-Entwürfen, Konzepten.
- semantAH indexiert ausgewählte Bereiche und erzeugt `insights.daily`.
- Timer/Jobs synchronisieren Vault und Fleet (z. B. Snapshots, Index-Rebuild).

**Nutzen:**
vault-gewebe ist das **assoziative Gedächtnis** – alles, was noch kein Code ist,
aber schon mehr als eine Idee.

---

### 2.10 weltgewebe – öffentliche Web-Schicht

**Repo:** `heimgewebe/weltgewebe`

- Docs-first Web-Projekt (SvelteKit + Rust/Axum + Postgres, JetStream, Caddy).
- Dient als **öffentliche Oberfläche** für Teile des Heimgewebes, mit klaren Gates
(A–D), welche Daten überhaupt hinaus dürfen.

**Nutzen:**
weltgewebe ist die **Haut** nach außen: nur das, was durch die Gates geht,
wird öffentlich sichtbar.

---

### 2.11 tools – gemeinsame Werkzeuge

**Repo:** `heimgewebe/tools`

- Enthält:
  - Merging-Tools (z. B. repomerger, wc-merger) zur Snapshot-Erstellung.
  - Hilfsskripte für Fleet-weit wiederkehrende Aufgaben.
- Wird von metarepo/wgx genutzt, um Org-Assets zu generieren (z. B. Tabellen aus `repos.yml`).

**Nutzen:**
tools ist der **Werkzeugkoffer** – alles, was mehrfach vorkommt, aber kein
eigenes „Organ“ ist.

---

### 2.12 Reflektions- und Meta-Organe

#### sichter

**Repo:** `heimgewebe/sichter`

- Automatisierte PR-Checks, Review-Heuristiken, Metriken.
- Produziert Insights, die in `insights.schema.json` passen.

#### mitschreiber

**Repo:** `heimgewebe/mitschreiber`

- Hilft beim Erstellen von Protokollen, Notizen, Texten auf Basis von Events und
semantischen Kontexten.

#### heimgeist

**Repo:** `heimgewebe/heimgeist`

- Meta-Agent, der über Events, Insights und Policies nachdenkt.
- Langfristig: „Bewusstseins-Schicht“ des Heimgewebes.

#### plexer

**Repo:** `heimgewebe/plexer`

- „Kreuzschiene“ für Ströme: verteilt Befehle und Events an die richtigen Organe.

**Nutzen insgesamt:**
Diese Repos sind das **Meta-Nervensystem**: sie schauen aufs Ganze,
formulieren Einsichten und helfen, nicht immer dieselben Fehler zu machen.

---

## 3. Typische Workflows (How-Tos)

### 3.1 Neues Repo in die Fleet aufnehmen

1. Repo in `heimgewebe` Organisation anlegen.
2. Im metarepo in der Repo-Matrix eintragen (Rolle, Status).
3. `.wgx/profile.yml` definieren (Sprache, Tests, CI-Erwartungen).
4. Reusable Workflows aus metarepo einbinden:
   - `wgx-metrics.yml` für Metrics-Snapshots.
   - Guard/Smoke (falls vorhanden) für Basis-Checks.

Ergebnis: das Repo wird automatisch in Fleet-Metriken und Leitstand-Sichten auftauchen.

---

### 3.2 Metrics-Snapshot eines Repos erzeugen

1. In der CI des Repos:

   ```yaml
   jobs:
     metrics:
       uses: heimgewebe/metarepo/.github/workflows/wgx-metrics.yml@contracts-v1
   ```

2. Optional: post_url setzen, damit der Snapshot direkt in eine chronik/leitstand-Ingest-Route wandert.

---

### 3.3 Tägliche Vault-Insights erzeugen

1. Vault-Pfad über VAULT_ROOT setzen.
2. semantAH-Script laufen lassen (z. B. per Timer):

   ```bash
   export VAULT_ROOT=/pfad/zum/vault
   python scripts/export_insights.py
   ```

3. Ergebnis:
   - `$VAULT_ROOT/.gewebe/insights/daily/YYYY-MM-DD.json`
   - `$VAULT_ROOT/.gewebe/insights/today.json`
4. hausKI/Leitstand nutzen diese Dateien, um „Heute im Vault“ zu zeigen – im Schema von `insights.daily.schema.json`.

---

## 4. Verdichtete Essenz

- metarepo definiert Contracts und Reusable CI.
- wgx führt Befehle Fleet-weit konsistent aus.
- hausKI, semantAH, chronik bilden das Gehirn + Gedächtnis.
- leitstand und weltgewebe sind die Augen & Anzeigen.
- aussensensor, heimlern, vault-gewebe, sichter, mitschreiber, heimgeist, plexer
sorgen für Wahrnehmung, Politik, Reflexion und Text.

Heimgewebe wird benutzbar, wenn:

Contracts im metarepo + wgx-Kommandos + chronik-Events + semantAH-Insights
→ regelmäßig laufen und im Leitstand sichtbar werden.

---

## 5. Ungewissheitsanalyse

- Unsicherheitsgrad: ca. 0,3
- Mögliche Abweichungen:
  - Repo-Struktur kann sich seit dem letzten Merge geändert haben.
  - Einige Features (leitstand-UI, heimgeist-Core-Loop) sind noch konzeptionell
und ggf. nur teilweise umgesetzt.
  - Die hier genannten CI-Snippets basieren auf der aktuellen
`wgx-metrics.yml`-Struktur; künftige Versionen könnten Inputs/Defaults ändern.

Trotzdem ist das README eine brauchbare Landkarte, um im Heimgewebe
nicht mehr ständig in den Gedärmen des Organismus nach der richtigen Datei zu suchen.
