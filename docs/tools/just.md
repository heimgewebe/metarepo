# just – Kurzüberblick im Heimgewebe

Dieses Projekt nutzt [`just`](https://github.com/casey/just) als Kommando-Orchestrator.
Die Upstream-Langdoku liegt extern; hier nur das Nötigste für den lokalen Gebrauch.

## Typische Rezepte im metarepo

- `just list` – verfügbare Rezepte
- `just up` – Templates & Reusable Workflows in Ziel-Repos ausrollen  
  - Dry-Run: `WGX_DRY_RUN=1 just up`
- `just smoke` – schneller Fleet-Health-Check

> Hinweis: deterministische Tool-Versionen via `scripts/tools/yq-pin.sh` und `toolchain.versions.yml`.
