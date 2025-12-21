# ADR-0027 Rename contracts to contracts-mirror

Status: accepted
Datum: 2025-12-21
Betroffene Repos:
- metarepo
- contracts-mirror (ehemals contracts)
- alle Domain-Repos

---

## 1. Kontext

Im Heimgewebe gab es bisher Verwirrung um den Begriff "contracts":
1. Das Verzeichnis `contracts/` im metarepo (Single Source of Truth, siehe ADR-0007).
2. Das Repository `heimgewebe/contracts` (Mirror für externe Konsumenten / Protobuf).

Diese Namenskollision führte zu Drift in der Dokumentation und Missverständnissen bei Menschen und Agenten ("Schau ins contracts-Repo" vs. "Schau in metarepo/contracts").

## 2. Entscheidung

Das Repository `heimgewebe/contracts` wird offiziell in **`heimgewebe/contracts-mirror`** umbenannt (bzw. dokumentarisch so geführt, falls der GitHub-Name aus technischen Gründen bleibt).

In der Dokumentation gilt:
- **`contracts`** bezieht sich auf das Konzept oder das Verzeichnis im metarepo (`metarepo/contracts/`).
- **`contracts-mirror`** bezieht sich auf das spezifische Repository für externe APIs.

## 3. Umsetzung

1. **Dokumentation:** Alle Referenzen auf das Repository werden in `contracts-mirror` geändert.
2. **Fleet-Definition:** In `fleet/repos.yml` heißt das Repo `contracts-mirror`.
3. **Guard:** Ein CI-Guard verhindert, dass `contracts` als Repository-Name in neuen Dokumenten verwendet wird (außer in historischen Archiven).

## 4. Konsequenzen

- Klarere Unterscheidung zwischen SSOT (metarepo) und Artefakt (mirror).
- Weniger Halluzinationen bei KI-Agenten bezüglich des Quellorts von Schemas.
- Historische ADRs (z. B. 0007) erhalten einen Header-Vermerk.
