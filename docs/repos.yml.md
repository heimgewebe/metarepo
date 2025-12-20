# repos.yml – Fleet-Konfiguration

Die **Fleet** umfasst alle Repositories, die operativ über WGX und Contracts
gesteuert werden sollen.

**Wichtig:**
Die Fleet ist **nicht** identisch mit „allen öffentlichen Repos der Organisation“.

Es gibt drei Klassen:
1. **Core-Fleet**: Repos in `repos:`
2. **Related**: Repos in `static.include`
3. **Private**: niemals in der Fleet

Beispiel:

```yaml
static:
  include:
    - name: weltgewebe
      url: "https://github.com/heimgewebe/weltgewebe"
      description: "Dokumentation/extern"
      status: "related"
  # private Repositories:
  # - vault-gewebe (nie Fleet)



repos:
  - name: metarepo
  - name: wgx
  - name: contracts-mirror
  - name: webmaschine
  - name: hausKI
  - name: hausKI-audio
  - name: heimlern
  - name: semantAH
  - name: aussensensor
  - name: chronik
  - name: tools
  - name: mitschreiber
  - name: sichter
  - name: leitstand
```
