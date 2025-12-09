# Contracts: Versionierung & Deprecations

Die Schemas im Ordner [`contracts/`](../contracts) werden über Fleet-Tags verteilt, damit Producer- und Consumer-Repos synchron bleiben. Dieser Leitfaden fasst die laufende Praxis aus [`docs/contracts.md`](./contracts.md) zusammen.

## Release-Kanäle

| Kanal | Zweck | Inhalt |
| --- | --- | --- |
| `contracts-v1` (Tag) | Freeze für alle produktiven Schemas und Reusable Workflows | `contracts/*.schema.json`, `.github/workflows/reusable-validate-jsonl.yml`, `.github/workflows/wgx-metrics.yml` |
| Default-Branch (`main`/`work`) | Vorbereitung auf nächste Version | Neue Schemas, Dokumentation, Rollout-Checklisten |

## Tagging & Nutzung
- Stabile Schemas werden nach Review auf einen Release-Branch (`chore/fleet-contracts-v1`) gehoben und anschließend als Tag `contracts-v1` veröffentlicht.
- Downstream-Workflows pinnen strikt auf `@contracts-v1`, um Breaking-Changes zu vermeiden.
- Der Reusable-Workflow [`reusable-validate-jsonl.yml`](../.github/workflows/reusable-validate-jsonl.yml) ist Teil des Tags und validiert JSONL-Feeds gegen die Schemas.

### Beispiele (Pinning)
```yaml
uses: heimgewebe/metarepo/.github/workflows/reusable-validate-jsonl.yml@contracts-v1
with:
  schema_url: https://raw.githubusercontent.com/heimgewebe/metarepo/contracts-v1/contracts/aussen.event.schema.json
```

## Deprecation-Fenster
- `contracts-v1` bleibt mindestens bis **2026-03** gültig.
- Breaking Changes wandern in einen neuen Branch/Tag `contracts-v2` (Rollout via `just fleet open-prs contracts-v2` o. Ä.).
- Für Hotfixes wird temporär `contracts-v1-hotfix` genutzt und anschließend wieder gelöscht.

## Pflegezyklus
- Vor jedem Fleet-Sync `just wgx plan` → prüfen, welche Repos Contracts konsumieren.
- `just fleet open-prs contracts-v1` stößt im ganzen Verbund Update-PRs an, sobald ein neuer Tag veröffentlicht ist.
- Rollout-Reihenfolge siehe [`docs/contracts.md`](./contracts.md#rollout-checkliste) (Producer → Consumer → Policies).
