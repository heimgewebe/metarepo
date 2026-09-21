# Heimgewebe – Nutzung & täglicher Betrieb

Heimgewebe ist ein verteiltes System aus mehreren Repos, das zusammen wie ein
autopoetischer KI-Organismus funktioniert:

- **metarepo** – Control-Plane (Contracts, CI-Vorlagen, Fleet-Definition)
- **wgx** – Werkzeugkasten und Fleet-Motorik
- **semantAH** – semantischer Index und Insights
- **chronik** – Ereignisspeicher (Event-Log, Audit)
- **leitstand** – UI / Dashboard
- **repoground** und **plexer** – verifizierbarer Kontext und Routing
- **commonThing** – verwandte öffentliche Web-Schicht

Die physisch gelöschten Repositories HausKI, Aussensensor, Vault-Gewebe,
Mitschreiber, Heimgeist, Heimlern und Sichter gehören nicht mehr zur aktiven Fleet.
Historische Verträge und Evidenz dürfen ihre Namen weiterhin als Provenienz führen.

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
Aktive Repos wie semantAH, chronik und plexer sind Producer oder
Consumer dieser Datenströme.

### 1.2 Typischer Tagesablauf (Operator-Sicht)

Ganz grob:

1. **Fleet-Status prüfen**
   - GitHub Actions → `wgx-metrics` und CI-Workflows beobachten.
   - Optional: Metrics-Snapshots an eine Ingest-URL posten (chronik/leitstand).

2. **Wissenslage checken**
   - `semantAH` erzeugt tägliche Vault-Insights nach
     `contracts/insights.daily.schema.json`.
   - Leitstand kann `topics`, `questions` und `deltas` daraus visualisieren.

3. **Events & Incidents ansehen**
   - `chronik` speichert Events im Format `event.line.schema.json`.
   - Leitstand liest daraus Dashboards und Tages-Digests.

4. **Arbeit an Repos**
   - WGX-Befehle nutzen (`wgx guard`, `wgx metrics snapshot` etc.).
   - aktuelle Operator- und Review-Pfade für Prüfaufgaben nutzen; plexer routet unterstützte Ströme.

Kurzfassung für Dummies:
> Heimgewebe ist ein Haufen Repos, die so tun, als wären sie ein Körper.
> metarepo ist das Regelbuch, wgx die Muskeln, semantAH das Bedeutungs-Gedächtnis,
> chronik das Tagebuch und leitstand die Anzeige.

---

## 2. Feature-Übersicht nach Repo (mit Links)

> Hinweis: Die GitHub-Links nehmen `heimgewebe` als Organisation an.

### 2.1 Control-Plane (metarepo)

**Repo:** `heimgewebe/metarepo`

- **Repo-Matrix & Fleet-Übersicht**
  - Welche Repos es gibt, ihre Rolle (z. B. memorativ, semantisch, politisch) und ihr Reifegrad.
  - Nutze sie als Einstieg, um zu verstehen, welches Repo wofür zuständig ist.

- **Contracts (Schemas)**
  - `contracts/event.line.schema.json` – gemeinsames Event-Schema für chronik-kompatible Ereignisse.
  - `contracts/insights.daily.schema.json` – Schema für semantAH Daily-Insights.
  - `contracts/insights.schema.json` – Review-Insights (z. B. aus semantAH).
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

### 2.3 HausKI – historische Referenz

Das frühere Repository `heimgewebe/hausKI` ist physisch gelöscht und besitzt
keine aktive Runtime-, Orchestrierungs- oder Consumer-Autorität mehr.

Historische Contracts, Tests und Evidenz dürfen HausKI weiterhin nennen, wenn
der historische Status ausdrücklich erkennbar ist.

---

### 2.4 semantAH – semantischer Index & Insights

**Repo:** `heimgewebe/semantAH`

- Producer für:
  - `insights.daily` – Tages-Zusammenfassung des Wissenszustands, Schema siehe Contracts.
  - `insights` – Review-Insights (z. B. aus Code-Analyse).
- Arbeitet gegen konfigurierte Vault-Pfade und andere Quellen; daraus folgt keine
  Abhängigkeit vom gelöschten Repository Vault-Gewebe.

**Nutzen:**
semantAH beantwortet die Frage: **„Was ist gerade wichtig?“**
Leitstand kann diese Informationen darstellen; weitere Consumer binden sich über
aktuelle Contracts und den Systemkatalog.

---

### 2.5 chronik – Ereignisspeicher

**Repo:** `heimgewebe/chronik`

- Speichert Events im JSONL-Format gemäß `event.line.schema.json`.
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

### 2.7 Aussensensor – historische Referenz

Das frühere Repository `heimgewebe/aussensensor` ist physisch gelöscht.
Seine früheren Event-Verträge bleiben nur als historische Provenienz erhalten;
es ist kein aktueller Feed-, Telemetrie- oder Producer-Pfad.

---

### 2.8 Heimlern – historische Policy-Referenz

Das frühere Repository `heimgewebe/heimlern` ist physisch gelöscht.
Erhaltene Policy- und Bandit-Evidenz dient ausschließlich als historischer Beleg.
Es besitzt keine aktive Runtime-, Routing-, Queue- oder Produktionsautorität;
aktuelle Zuständigkeiten stehen im Systemkatalog.

---

### 2.9 Vault-Gewebe – historische Referenz

Das frühere Repository `heimgewebe/vault-gewebe` ist physisch gelöscht.
SemantAH kann weiterhin konfigurierte lokale Vault-Pfade indexieren; daraus darf
keine aktuelle Repository-Abhängigkeit zu Vault-Gewebe abgeleitet werden.

---

### 2.10 commonThing – öffentliche Web-Schicht

**Repo:** `heimgewebe/commonthing`

- Docs-first Web-Projekt (SvelteKit + Rust/Axum + Postgres, JetStream, Caddy).
- Dient als **öffentliche Oberfläche** für Teile des Heimgewebes, mit klaren Gates
(A–D), welche Daten überhaupt hinaus dürfen.

**Nutzen:**
commonThing ist die **Haut** nach außen: nur das, was durch die Gates geht,
wird öffentlich sichtbar.

---

### 2.11 RepoGround – verifizierbarer Codebase-Kontext

**Repo:** `heimgewebe/repoground`

- Enthält:
  - Merging-Tools (z. B. repomerger, wc-merger) zur Snapshot-Erstellung.
  - Scanner-/Merger-Läufe für Fleet-weite Snapshot- und Report-Bildung.
- Wird von metarepo/wgx genutzt, um Org-Assets zu generieren (z. B. Tabellen aus `repos.yml`).

**Nutzen:**
RepoGround erzeugt **verifizierbaren Codebase-Kontext**: konsistente Snapshots
und mehrstufige Artefakte für Analyse, Reflexion und Agentenbetrieb.

---

### 2.12 Reflektions- und Meta-Organe

#### Sichter – historisch

Das frühere Repository `heimgewebe/sichter` wurde physisch gelöscht. Es besitzt keine aktuelle Review-, PR-Automations-, Fleet- oder Runtime-Autorität. Verbliebene Contracts und Dokumente dienen ausschließlich als historische Provenienz.

#### Mitschreiber – historisch

Das frühere Repository `heimgewebe/mitschreiber` ist physisch gelöscht.
Verbliebene Contracts oder Beispiele sind historische Provenienz, keine aktuelle
Schreib- oder Consumer-Fläche.

#### Heimgeist – historisch

Das frühere Repository `heimgewebe/heimgeist` ist physisch gelöscht.
Es besitzt keine aktive Meta-Agent-, Runtime- oder Consumer-Autorität.

#### plexer

**Repo:** `heimgewebe/plexer`

- „Kreuzschiene“ für Ströme: verteilt Befehle und Events an die richtigen Organe.

**Nutzen insgesamt:**
Plexer bleibt eine aktive Routing-Fläche. Sichter, Mitschreiber und Heimgeist sind nur noch historische Referenzen.

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
4. Leitstand kann diese Dateien im Schema von `insights.daily.schema.json` darstellen.

---

## 4. Verdichtete Essenz

- metarepo definiert Contracts und Reusable CI.
- wgx führt Befehle Fleet-weit konsistent aus.
- semantAH und chronik bilden semantisches Gedächtnis und Ereignisspur.
- leitstand und commonThing sind Anzeige- und Web-Flächen.
- plexer liefert aktive Routing-Funktionen; Prüf- und Review-Autorität folgt den aktuellen Operatorverträgen.
- HausKI, Aussensensor, Vault-Gewebe, Mitschreiber, Heimgeist, Heimlern und Sichter
  sind physisch gelöscht; erhaltene Nennungen dienen nur historischer Evidenz.

Heimgewebe wird benutzbar, wenn:

Contracts im metarepo + wgx-Kommandos + chronik-Events + semantAH-Insights
→ regelmäßig laufen und im Leitstand sichtbar werden.

---

## 5. Ungewissheitsanalyse

- Unsicherheitsgrad: ca. 0,3
- Mögliche Abweichungen:
  - Repo-Struktur kann sich seit dem letzten Merge geändert haben.
  - Einige Leitstand- und Integrationsfunktionen können noch konzeptionell oder
    nur teilweise umgesetzt sein.
  - Die hier genannten CI-Snippets basieren auf der aktuellen
`wgx-metrics.yml`-Struktur; künftige Versionen könnten Inputs/Defaults ändern.

Trotzdem ist das README eine brauchbare Landkarte, um im Heimgewebe
nicht mehr ständig in den Gedärmen des Organismus nach der richtigen Datei zu suchen.
