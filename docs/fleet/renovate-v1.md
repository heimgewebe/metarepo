# Renovate Fleet V1

Stand: 2026-07-23

## Zweck

Renovate V1 ist der Fleet-weite Produzent regulärer Dependency-Version-Update-PRs.
Fleet-Mitgliedschaft bleibt ausschließlich in `fleet/repos.yml`; die Renovate-Policy
projiziert daraus den aktiven Runtime-Scope und definiert keine zweite Fleet.

Renovate darf Dependencies erkennen sowie Update-Branches und Pull Requests erzeugen.
Renovate darf nicht automatisch mergen, Bureau-Tasks oder Queue-Zustand erzeugen,
Deployments ausführen oder GitHub-/CI-/Grabowski-Merge-Gates ersetzen.

## Direkter Cutover

Die frühere Pilotstaffelung ist aufgehoben. Die selbst gehostete Renovate-Runtime auf
dem Heim-PC verwaltet alle 18 aktiven Fleet-Repositories. Der Scope wird deterministisch
aus `fleet/repos.yml` und `automation/renovate/dependency-updates.v1.yml` erzeugt.
Archivierte Referenzen und `fleet: false` bleiben ausgeschlossen.

Für die fünf Repositories mit bestehenden Dependabot-Version-Updates gilt die
Cutover-Reihenfolge weiterhin fail-closed:

1. Renovate-Lookup im Dry-Run für den vollständigen Fleet-Scope belegen.
2. Überlappende Dependabot-Version-Update-Einträge entfernen bzw. deaktivieren.
3. Den Single-Producer-Zustand live verifizieren.
4. Erst danach Renovate ohne Dry-Run starten.

Mitschreiber hat keine Dependabot-Version-Updates; seine bestehende Renovate-Konfiguration
wird vor dem ersten schreibenden Fleet-Lauf auf den aktuellen Custom-Manager-Vertrag
umgestellt und sämtliches Automerge entfernt.

Dependabot Security Updates und Security Alerts bleiben ein getrennter Security-Pfad.
Der Versions-Cutover behauptet nicht, diesen Pfad zu ersetzen oder abzuschalten.

## Kanonische Dateien

- `fleet/repos.yml`: einzige normative Fleet-Mitgliedschaft.
- `automation/renovate/dependency-updates.v1.yml`: operative Provider- und Cutover-Policy.
- `automation/renovate/default.json`: gemeinsamer Renovate-Preset mit `automerge: false`.
- `automation/renovate/expected-scope.v1.json`: deterministische, nicht-authoritative Scope-Projektion.
- `automation/renovate/runtime-config.cjs`: self-hosted Renovate-Konfiguration; liest die Scope-Projektion.
- `automation/renovate/run-fleet.sh`: gepinnter Runtime-Wrapper.
- `automation/renovate/install-local-runtime.sh`: commitgebundene lokale Runtime-Installation.
- `automation/renovate/systemd/renovate-fleet.{service,timer}`: täglicher Fleet-Lauf.
- `scripts/fleet/renovate_policy.py`: fail-closed Policy- und Scope-Validierung.

## Runtime und Zugang

Die Runtime läuft lokal auf dem Heim-PC und nutzt den vorhandenen `gh`-Login nur zur
Laufzeit. `run-fleet.sh` liest `gh auth token`, exportiert den Wert ausschließlich in die
Renovate-Prozessumgebung und persistiert den Token weder im Repository noch in der
Renovate-Konfiguration. Der aktuelle Runtime-Pfad ist auf eine immutable Release-Kopie
unter `~/.local/share/renovate-fleet/releases/<commit>` gebunden; `current` ist nur ein
atomar umschaltbarer Symlink.

Der Runtime-Scope ist eine explizite `repositories`-Liste aus
`expected_renovate_repositories`; `autodiscover` und Renovate-Onboarding sind deaktiviert.
Damit kann ein Organisation-weites GitHub-Token nicht automatisch Repositories außerhalb
der kanonischen Fleet in den Update-Scope ziehen.

Renovate ist auf Version `42.99.0` gepinnt. Eine spätere Versionsanhebung ist eine
reviewte Änderung dieses Wrappers.

## Preset-Grenzen

Der gemeinsame Preset:

- erweitert `config:recommended`;
- setzt `automerge: false`;
- begrenzt PR-, Branch- und Stundenparallelität auf höchstens zwei;
- hält Major-Updates getrennt;
- gruppiert zentral nur Patch-/Minor-Updates für GitHub Actions;
- enthält keine Post-Upgrade-Command-Ausführung.

Repo-spezifische Konfiguration darf diese Sicherheitsgrenzen nicht durch Automerge
unterlaufen. Vor dem ersten schreibenden Lauf werden bekannte lokale Abweichungen wie
die alte Mitschreiber-Konfiguration korrigiert.

## Single-Producer-Vertrag

Pro Repository und Dependency-Scope darf genau ein aktiver Produzent regulärer
Version-Update-PRs existieren. Die sechs expliziten Cutover-Repositories modellieren den
bekannten vorherigen Producer-Zustand; der Selector `remaining-eligible-active-fleet`
leitet die übrigen aktiven Fleet-Repositories direkt aus `fleet/repos.yml` ab. Eine
explizite zweite Vollkopie der Fleet bleibt verboten.

Die Scope-Projektion muss alle 18 aktiven Fleet-Repositories in
`expected_renovate_repositories` enthalten und darf für die selbst gehostete Runtime
keinen Hosted-App-Scope behaupten.

## Scheduling

Nach dem ersten erfolgreichen schreibenden Cutover-Lauf wird `renovate-fleet.timer`
aktiviert. Der Timer läuft täglich um 05:17 Uhr mit bis zu 15 Minuten Randomisierung.
Ein Lauf ist `oneshot`, hat ein Vier-Stunden-Limit und besitzt keine Merge-Autorität.

## Validierung

`just renovate-policy-check` prüft unter anderem:

- Policy gegen die aktive Fleet aus `fleet/repos.yml`;
- Ausschluss archivierter und `fleet: false` Repositories;
- keine explizite zweite vollständige Fleet-Liste;
- keine zwei gleichzeitig als aktiv deklarierten Version-Update-Produzenten;
- vollständige abgeleitete Renovate-Projektion für alle 18 aktiven Fleet-Repositories;
- `automerge: false`, Major-Isolation und begrenzte Parallelität;
- unveränderte 30-Tage-Baseline;
- bytegenaue Reproduzierbarkeit der Scope-Projektion.

Vor dem echten Cutover ist zusätzlich ein Renovate-Lookup-Dry-Run erforderlich. Danach
werden die betroffenen Dependabot-Konfigurationen PR-gebunden geändert und der
Single-Producer-Zustand erneut live gelesen.

## Rollback

Die lokale Runtime kann durch Stoppen/Deaktivieren von `renovate-fleet.timer` und
`renovate-fleet.service` sofort angehalten werden. Der vorherige Runtime-Release bleibt
unter `~/.local/share/renovate-fleet/releases/` erhalten und kann durch Rücksetzen des
`current`-Symlinks wieder aktiviert werden.

Für Repositories, deren Dependabot-Version-Updates bereits entfernt wurden, besteht der
Rollback aus dem Revert des jeweiligen reviewten Cutover-Commits. Anschließend muss live
belegt werden, dass wieder exakt ein Version-Update-Produzent aktiv ist. Bureau-,
Chronik- und Git-Historie werden nicht umgeschrieben.
