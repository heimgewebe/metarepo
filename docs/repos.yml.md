# repos.yml – Fleet-Konfiguration

> **⚠️ SOURCE OF TRUTH NOTICE**
> The canonical definition of the Fleet is located in `fleet/repos.yml`.
> All lists of repositories in this documentation are derived or exemplary.
> Do not edit repository lists manually in Markdown files.

Die **Fleet** umfasst alle Repositories, die operativ über WGX und Contracts
gesteuert werden sollen.

**Wichtig:**
Die Fleet ist **nicht** identisch mit „allen öffentlichen Repos der Organisation“.

Es gibt drei Klassen:
1. **Core-Fleet**: Repos in `repos:`
2. **Related**: Repos in `static.include`
3. **Private**: niemals in der Fleet

Eine aktuelle, generierte Übersicht befindet sich in:
👉 **[docs/_generated/fleet.md](_generated/fleet.md)**

---

Die Definition in `fleet/repos.yml` ist maßgeblich.
