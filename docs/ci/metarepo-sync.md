<!-- managed-by: metarepo-sync -->
# Metarepo Sync

Dieses Dokument beschreibt den Sync-Mechanismus, mit dem kanonische Dateien aus dem `metarepo`
in Fleet-Repositories repliziert werden.

## Manifest

Das Manifest liegt im `metarepo` unter:

- `sync/metarepo-sync.yml`

Jeder Eintrag definiert:
- `source`: Pfad im metarepo (kanonisch)
- `targets`: Zielpfade in Fleet-Repos
- `mode`: `copy` (verwaltet) oder `copy_if_missing` (nur initial)

## Managed Marker (Safety Gate)

Updates (`mode: copy`) werden nur durchgeführt, wenn die Ziel-Datei den Marker enthält:

- `managed-by: metarepo-sync`

**Wichtig:** Der Sync-Engine prüft nur die ersten Zeilen der Datei.
Der Marker muss daher oben im Datei-Header bleiben (nicht nach unten verschieben).

## Sync Modes

- `dry_run`: erzeugt nur Reports, keine Änderungen
- `apply`: schreibt Änderungen (bei UPDATE zusätzlich mit Backup)

## Report / Health Integration

Der Sync schreibt pro Repo einen Report:

- `.gewebe/out/sync.report.json`

Dieser Report ist die Grundlage für Repo-Health/Statusanzeigen (ok/warn/unknown).
