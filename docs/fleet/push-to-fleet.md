# Push to Fleet (Wave-1)

**Ziel:** `agent-kit` + Contracts in Ziel-Repos als PR ausrollen.

> **Hinweis:** `push_template.py` benötigt **PyYAML**. Lokal:  \
> `python3 -m pip install --user pyyaml`  \
> Just-Targets: `just fleet.push-dry repo=ORG/REPO` (Trockenlauf) oder `just fleet.push[-all]`.

## Voraussetzungen
- GitHub CLI `gh` (`gh auth status` = ok)
- Python ≥ 3.11
- In diesem Repo vorhanden:
  - `templates/agent-kit/**`
  - `contracts/agent.tool.schema.json`

## Repos konfigurieren
Bearbeite `fleet/repos.yml`:
```yaml
repos:
  - name: heimgewebe/hausKI
    default_branch: main
  - name: heimgewebe/semantAH
    default_branch: main
  - name: heimgewebe/mitschreiber
    default_branch: main
  - name: heimgewebe/chronik
    default_branch: main
  - name: heimgewebe/heimlern
    default_branch: main
  - name: heimgewebe/aussensensor
    default_branch: main
```

## Ausführen
Ein Repo:
```bash
just fleet.push repo=heimgewebe/hausKI
```

Alle Repos:
```bash
just fleet.push-all
```

## Was passiert
1. `gh repo clone` in ein Temp-Verzeichnis  
2. Branch `feat/agents-and-contracts-wave-1` anlegen  
3. Kopieren:
   - `templates/agent-kit/**` → `<repo>/templates/agent-kit/**`
   - `contracts/agent.tool.schema.json` → `<repo>/contracts/agent.tool.schema.json`
   - **wenn Repo = `chronik`**: zusätzlich `contracts/intent_event.schema.json`
4. Commit & Push
5. PR eröffnen (Label: `fleet/wave-1`)

## Hinweise
- Idempotent für wiederholtes Ausrollen (überschreibt nur unterhalb der Zielpfade).
- Kein Build/CI-Eingriff im Zielrepo, außer es gibt bereits agent-bezogene CI.
