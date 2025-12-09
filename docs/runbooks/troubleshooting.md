# Troubleshooting (Top-Fleet-Issues)

Kurzer Spickzettel für die häufigsten Stolpersteine rund um Fleet-Sync & WGX.

## 1. `wgx` nicht im PATH
- Symptom: CI-Job bricht mit `command not found: wgx` ab.
- Fix: Installationsschritte aus der [WGX-Doku](https://github.com/heimgewebe/wgx) in den Workflow einbauen (z. B. Setup-Script
  vor den Guard-Checks ausführen).

## 2. CI ohne `uv`
- Symptom: Python-Projekte laufen in der CI ohne Abhängigkeits-Cache.
- Fix: Vor dem `just`-Aufruf `pipx install uv` (oder entsprechendes Setup) ausführen und den Cache-Pfad als `actions/cache`
  Schritt hinterlegen.

## 3. `lychee` / `cspell` langsam
- Symptom: PR-Checks dauern >10 Minuten.
- Fix: Link-/Spell-Checks in separate Workflows auslagern oder via Workflow-Inputs deaktivierbar machen; Ergebnisse in Nightly
  Pipelines konsolidieren.

## 4. Template-Drift nach lokalem Hotfix
- Symptom: Sub-Repo hat Änderungen, die beim nächsten Sync überschrieben würden.
- Fix: `scripts/sync-templates.sh --pull-from <repo> --pattern "templates/**"` nutzen, Änderung im metarepo kuratieren.

## 5. `gh` Rate-Limits
- Symptom: `scripts/wgx list` scheitert mit API-Errors.
- Fix: `gh auth login` mit PAT, `GH_TOKEN` als Secret im CI setzen.

## 6. Merge-Konflikt beim Stub-Dokument
- Symptom: `docs/wgx-konzept.md` wird lokal erweitert.
- Fix: Hinweis auf Stub-Policy geben, Ergänzungen in WGX-Repo verlagern.

## 7. Reports fehlen
- Symptom: `reports/` bleibt leer trotz Doctor-Lauf.
- Fix: Prüfe, ob `./scripts/wgx-doctor --repo <name> --verbose` erfolgreich durchlief (kein Clone-Error) und ob Unterschiede existierten.
  Ohne Drift wird kein Abschnitt erzeugt – dennoch entsteht eine leere Report-Datei. CI-Artefakte gezielt einsammeln.

## 8. `scripts/sync-templates.sh` meldet „Keine Repos in Datei“
- Symptom: `--repos-from` liefert keine Ziele.
- Fix: In `repos.yml` müssen unter `repos:` oder `static.include:` Einträge mit mindestens `name:` vorhanden sein (Kommentare zählen nicht).

## 9. SSH statt HTTPS erwartet
- Symptom: `scripts/wgx up` schlägt beim Klonen fehl.
- Fix: Stelle `git@github.com:...` Zugriff sicher (SSH-Key), oder passe Workflow auf HTTPS an (`GH_TOKEN`).

## 10. Fehlende Owner-Angabe
- Symptom: `scripts/wgx` gibt `owner=` leer aus.
- Fix: `github.owner` in `repos.yml` setzen oder `GITHUB_OWNER` exportieren.

## 11. Bats-Testregressionen nach Template-Updates
> Bats läuft bei uns mit Bash sowie `set -euo pipefail`. Fehlende Defaults schlagen daher sofort durch – die folgenden Snippets zeigen robuste Muster.

- Symptom: `tests/profile_parse_tasks.bats` (z. B. um Zeile 80) bricht mit `WGX_TASK_SAFE[safe_upper]: unbound variable` ab.
- Fix: Vor dem Zugriff auf assoziative Arrays die Existenz des Keys prüfen oder einen Default setzen, damit `set -u` nicht greift.

  ```bash
  if [[ -v WGX_TASK_SAFE[safe_upper] ]]; then
    assert_equal "1" "${WGX_TASK_SAFE[safe_upper]}"
  else
    echo "Key 'safe_upper' is not set in WGX_TASK_SAFE"
    exit 1
  fi
  ```

  Alternativ lässt sich der Fallback kurz mit `:` setzen:

  ```bash
  : "${WGX_TASK_SAFE[safe_upper]:=0}"
  ```

- Symptom: JSON-Assertions wie `tests/assertions.bats` (um Zeile 80) scheitern, wenn zusätzliche Keys vorhanden sind.
- Fix: Die Assertion auf Partial-Matches umstellen oder das erwartete JSON vollständig angeben.

  ```bash
  assert_output --partial '"a":2'
  ```

  ```bash
  # schlägt fehl, wenn weitere Keys wie "z" auftauchen
  assert_output '{"a":2}'
  ```

- Symptom: `tests/profile_tasks.bats` (z. B. um Zeile 150) meldet `raw_cmd=STR:echo 'a 'x y'` und verliert damit Quotes.
- Fix: Kommandos als Array übergeben oder beim Joinen `printf '%q '` verwenden (erfordert Bash; die Ausgabe lässt sich sicher erneut auswerten).

  ```bash
  raw_cmd=(echo "a # b" "x y")
  "${raw_cmd[@]}"
  ```

  ```bash
  printf '%q ' "${raw_cmd[@]}"
  ```

- Symptom: Mehrere Bats-Tests (z. B. `tests/reload.bats`, `tests/sync.bats`) schlagen mit `[ "$status" -eq 0 ]` fehl.
- Fix: Vorbereitende Abhängigkeiten im Test-Setup sicherstellen (Services, Mock-Skripte) und bei Bedarf `set -x` aktivieren, um den fehlgeschlagenen Befehl zu identifizieren.

  ```bash
  set -x
  run ./scripts/wgx-doctor --repo demo --verbose
  set +x
  ```

Weitere Issues? → GitHub Issue im metarepo öffnen und in der nächsten Fleet-Runde dokumentieren.

Generelle Konventionen und Good Practices für neue Bats-Suites sammeln wir perspektivisch in `docs/testing.md`.
