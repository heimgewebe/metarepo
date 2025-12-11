# Heimgewebe Agent-Mode

Der Agent-Mode definiert Rahmenbedingungen, unter denen der GitHub
Copilot Coding Agent sicher und deterministisch mit diesem Repository
arbeiten kann.

Kernidee:

* **Kein Netzwerkzugriff** aus Builds, Checks oder Tools, die im Agent
  ausgeführt werden.
* **Keine dynamischen Installationen** von Tools (z. B. `npm install`,
  `curl | bash`, `pip install`) zur Laufzeit.
* **Nur lokal vendorte oder vom Runner bereitgestellte Tools**.

Der Agent-Mode ist ein Zusatzmodus zu den normalen CI-Jobs. Er stellt
sicher, dass der Agent ausschließlich auf lokale Artefakte zugreifen
muss und nicht an Firewalls scheitert.

## 1. Invarianten im Agent-Mode

1. **Keine Outbound-HTTP-Calls** in:

   * `.github/workflows/*.yml`
   * `scripts/*.sh`, `scripts/*.bash`
   * `.wgx-tools/*` (soweit im Agent ausgeführt)

   Konkret verboten im Agent-Mode:

   * `curl http`, `curl https`
   * `wget http`, `wget https`
   * `http`-URLs zu `api.github.com`, `raw.githubusercontent.com`,
     Paketregistern etc.

2. **Keine dynamischen Installationen**:

   * Keine `npm install` / `pip install` / `go install` / `cargo install`
     direkt im Workflow.
   * Tools sollen entweder:
     * vom Runner kommen (z. B. systemweite `node`, `python3`),
     * oder lokal vendort sein (z. B. `.tools/ajv`, `.tools/bats`).

3. **Schemas, Contracts und Fixtures**:

   * JSON-Schemas (z. B. `knowledge.graph.schema.json`) liegen lokal
     im Repo (z. B. unter `contracts/` oder `json/`).
   * Kein `curl` auf `raw.githubusercontent.com` zum Laden von Schemas.

4. **Agent-Mode Schalter**

   * Für Skripte, die sowohl „normal“ als auch im Agent-Mode laufen
     sollen, gilt:

     * Wenn `${AGENT_MODE:-}` gesetzt und nicht leer ist → keine
       Netzwerkzugriffe, keine Installationen.
     * Remote-Teile werden übersprungen und stattdessen ein klarer
       Hinweis ausgegeben (`echo "Agent-Mode: skipping remote step"`).

## 2. Praktische Umsetzung

### 2.1. Vendoring von Tools

Beispiele für Tools, die im Agent-Mode lokal liegen sollten:

* `ajv` CLI (JSON-Schema-Validator)
* `bats` / `bats-core` (Shell-Tests)
* WGX-Hilfstools, soweit nicht bereits zentral installiert.

Empfohlenes Muster:

```text
.tools/
  ajv/
  bats/
  …
```

Skripte und Workflows referenzieren dann nur noch diese lokalen
Installationen.

### 2.2. Agent-Mode Guard

Dieser Repo enthält den Workflow
`.github/workflows/agent-mode-guard.yml` sowie das Skript
`scripts/agent-mode-check.sh`.

Der Guard prüft:

* ob in Workflows oder Scripts offensichtliche Netzwerkaufrufe zu
  `api.github.com`, `raw.githubusercontent.com` etc. vorkommen,
* ob `npm install` / `pip install` / `curl | bash` im Code auftauchen.

Der Guard soll nicht perfekt sein, sondern als Sicherheitsgurt dienen.

## 3. Verwendung

* Für Agent-Kompatibilitätsprüfungen `agent-mode-guard`-Workflow laufen
  lassen (manuell oder per Pull-Request).
* Neue Skripte/Workflows so bauen, dass sie mit gesetztem `AGENT_MODE`
  ohne Outbound-Network und ohne Installationen auskommen.
