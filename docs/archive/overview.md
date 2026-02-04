> **⚠️ ARCHIVE NOTICE**
> This document reflects a historical system overview.
> The canonical fleet definition is `fleet/repos.yml`.
> Lists of repositories below may be outdated.

# Heimgewebe – System Overview

Die folgende Masterliste beschreibt **alle Repositories des Heimgewebes**, gegliedert nach ihrer Rolle
im Organismus und ihrer Zugehörigkeit zur **Fleet**.

Es gibt drei Klassen:

**Core-Fleet**
→ Repos, die WGX-Profile, Contracts, Templates und Runbooks erhalten.

**Related**
→ Repos, die Teil des Ökosystems sind, aber *nicht* Fleet-pflichtig.

**Private**
→ Repos, die bewusst nicht in die Fleet aufgenommen werden.


## Core-Fleet

### metarepo

Control-Plane, Fleet-Konfiguration, Contracts, Templates.

### wgx

Fleet-Motor (CLI, Profiles, Doctor).

### contracts-mirror

Externe API-Contracts für die Heimgewebe-Ökosystem-Grenze (Mirror).

Dieses Repository enthält:

- Protobuf-APIs (z. B. `heimgewebe/aussen/v1`, `heimgewebe/heimlern/v1`)
- die dazugehörigen JSON-Mirror-Schemata unter `json/*.schema.json`

Interne Organismus-Contracts (z. B. `event.line`, `fleet.health`,
`os.context.*`, `policy.*`) liegen ausschließlich im **metarepo** im
Verzeichnis `contracts/` und werden von dort von der Fleet konsumiert.

### hausKI

KI-Kern (Rust GPU/CPU).

### hausKI-audio

Audio-Pipeline und Telemetrie.

### heimlern

Lern-/Policy-Schicht.

### semantAH

Embeddings, Wissensschicht.

### mitschreiber

Dialogische Schreib-/Semantikschicht.

### sichter

Review/Analyse-Agent (PR-Bewertungen, Checks).

### leitstand

UI/Dashboard.

### aussensensor

Event-Ingest aus der Außenwelt.

### chronik

Event-Persistenz, Audit-Log.

### tools

Universelle Skripte & Hilfsprogramme.

### heimgeist

Meta-Agent für Beobachtung / Orchestrierung.

### plexer

Routing/Orchestrierungs-Schicht zwischen Agents.

### heim-pc

Orientierungssystem für KI-Agenten / lokaler Anker (Tooling).


## Related

- weltgewebe — Dokumentation / Public Web / externe Signale (nicht Fleet)

## Private

- vault-gewebe — privater Obsidian-Vault (nie Fleet)

---

Alle Fleet-relevanten Repositories sind in `fleet/repos.yml` vollständig dokumentiert.
