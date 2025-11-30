# Kernkonzepte des Metarepo

Dieses Dokument beschreibt die grundlegende Architektur und die zentralen Prozesse des `metarepo`. Das Ziel ist es, ein konsistentes und zentral verwaltetes System über eine Flotte von Sub-Repositories zu schaffen.

## Metarepo-Architektur

Das `metarepo` dient als "Single Source of Truth" für kanonische Konfigurationen, die in andere Repositories (Sub-Repos) verteilt werden. Die Hauptkomponenten sind:

- **`templates/`**: Dieses Verzeichnis enthält die Vorlagen, die in die Sub-Repos synchronisiert werden. Dazu gehören CI/CD-Workflows, `Justfile`-Konfigurationen, Dokumentation und `.wgx/profile.yml`-Dateien.
- **`repos.yml`**: Die zentrale Inventarliste der Flotte. Diese Datei definiert, welche Repositories vom `metarepo` verwaltet werden, und enthält Metadaten wie den Namen, den Branch und die Abhängigkeiten.
- **`scripts/`**: Enthält die Orchestrierungs- und Synchronisationslogik. Das `wgx`-Skript ist das primäre Werkzeug für die Interaktion mit der Flotte.
- **`AGENTS.md`**: Definiert die Regeln und Prozesse für automatisierte Agenten (wie diesen), die im Repository arbeiten.

## Synchronisationsprozess

Der Abgleich von Konfigurationen zwischen dem `metarepo` und den Sub-Repos ist ein fundamentaler Prozess. Er folgt einem dialektischen Modell des Lernens und Verteilens.

### Push (Kanon → Sub-Repo)
Dies ist der Standardprozess, bei dem die kanonischen Vorlagen aus dem `metarepo` in die Sub-Repos verteilt werden. Der `wgx up`-Befehl automatisiert diesen Prozess:

1.  **Klonen**: Das Ziel-Repo wird temporär geklont.
2.  **Kopieren**: Die Vorlagen aus `templates/` werden in das geklonte Repo kopiert. Variablen (`{{REPO_NAME}}`) werden ersetzt.
3.  **Commit & PR**: Die Änderungen werden in einen neuen Branch committet, und ein Pull Request wird erstellt.

### Pull (Sub-Repo → Kanon)
In manchen Fällen werden Verbesserungen direkt in einem Sub-Repo entwickelt. Der `scripts/sync-templates.sh`-Befehl ermöglicht es, diese Änderungen zurück in das `metarepo` zu ziehen, um sie zu kuratieren und als neuen kanonischen Standard zu übernehmen.

### Drift
Als "Drift" wird der Zustand bezeichnet, in dem die Konfiguration eines Sub-Repos von der kanonischen Vorlage im `metarepo` abweicht. Werkzeuge wie `scripts/wgx-doctor` sind dazu gedacht, diesen Drift zu erkennen und zu melden.

## Die Rolle von `repos.yml`

Die `repos.yml`-Datei ist das Herzstück der Flottenverwaltung. Sie definiert den "Scope" der Operationen und ermöglicht eine präzise Steuerung der Synchronisation. Eine typische Struktur sieht wie folgt aus:

```yaml
github:
  owner: heimgewebe
  mode: github # 'github' für dynamische Listen, 'static' für feste

repos:
  - name: metarepo
    branch: main
  - name: wgx
    branch: main
```

- **`owner`**: Der GitHub-Organisationname.
- **`mode`**: Bestimmt, ob die Liste der Repos dynamisch von GitHub (`github`) oder aus der statischen Liste in `repos` (`static`) bezogen wird.
- **`repos`**: Eine Liste von Repository-Objekten, die den Namen und optional weitere Metadaten enthalten.

---

## Siehe auch

- [Templates](./templates.md) – Template-Verteilung und Drift-Kontrolle
- [Fleet Management](./fleet.md) – Fleet-Operationen im Überblick
- [WGX Konzept](./wgx-konzept.md) – Fleet-Motor und Kommandos
- [Architecture](./architecture.md) – Systemarchitektur
- [ADR-002: Distribution & Drift-Regeln](./adrs/002-distribution-drift.md) – Architekturentscheidung
