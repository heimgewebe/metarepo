# Heimgewebe Fleet – Kurzüberblick

> **Kernabgrenzung:** Die Heimgewebe-**Fleet** besteht aus den *Core-Repos*. Zusätzlich existieren verwandte Repos, die parallel entwickelt werden oder persönliche Daten enthalten, aber **nicht** zur Fleet zählen.

### Schichtenüberblick (v0.2)
+
+- 0 **Physisch:** WGX/OS/systemd
+- 1 **Semantisch:** semantAH
+- 2 **Operativ:** hausKI
+- 3 **Reflexiv:** sichter
+- 4 **Memorativ:** leitstand
+- 5 **Politisch-Adaptiv:** heimlern
+- 6 **Dialogisch-Semantisch:** mitschreiber, hausKI-audio
+
+**Nicht-Fleet:** `vault-gewebe` (privat) & `weltgewebe` (unabhängig)
+
## Rollen (Control vs. Ausführung)
- **metarepo** · Control-Plane, Verträge & Reusable Workflows (Tags wie `contracts-v1`)
- **wgx** · Motorik & PC-Wartung (führt Playbooks aus, liefert Metrics)
