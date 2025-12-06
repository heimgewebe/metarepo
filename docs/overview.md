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

- metarepo — Control-Plane, Fleet-Konfiguration, Contracts, Templates
- wgx — Fleet-Motor (CLI, Profiles, Doctor)
- contracts — zentrale JSON-Schemata für Agents & Events
- hausKI — KI-Kern (Rust GPU/CPU)
- hausKI-audio — Audio-Schicht (`depends_on: hausKI`)
- heimlern — Lern-/Policy-Schicht
- semantAH — Embeddings, Wissensschicht
- mitschreiber — dialogische Schreib-/Semantikschicht
- sichter — Review/Analyse-Agent (PR-Bewertungen, Checks)
- leitstand — UI/Dashboard
- aussensensor — Event-Ingest aus der Außenwelt
- chronik — Event-Persistenz, Audit-Log
- tools — universelle Skripte & Hilfsprogramme
- heimgeist — Meta-Agent für Beobachtung / Orchestrierung
- plexer — Routing/Orchestrierungs-Schicht zwischen Agents

## Related

- weltgewebe — Dokumentation / Public Web / externe Signale (nicht Fleet)

## Private

- vault-gewebe — privater Obsidian-Vault (nie Fleet)

---

Alle Fleet-relevanten Repositories sind in `fleet/repos.yml` vollständig dokumentiert.
