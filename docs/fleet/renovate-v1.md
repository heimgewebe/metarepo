# Renovate Fleet V1

Stand: 2026-07-23

## Zweck

Renovate V1 ist ein Fleet-gebundener Dependency-Sensor und PR-Produzent. Es ist
keine neue Control Plane. Fleet-Mitgliedschaft bleibt ausschließlich in
`fleet/repos.yml`; die Renovate-Policy beschreibt nur operative Rollout- und
Provider-Zustände für eine Teilmenge dieser Fleet.

Renovate darf in V1:

- bekannte Dependency-Manager auswerten;
- kompatible Patch-/Minor-Updates managerweise gruppieren;
- Update-Branches und Pull Requests erzeugen.

Renovate darf in V1 nicht:

- automatisch mergen;
- Bureau-Tasks, Queue-Einträge oder Claims erzeugen;
- Deployments oder Task-Verifikation ausführen;
- eine eigene Fleet-Mitgliedschaft definieren;
- GitHub-/CI- oder Grabowski-Head-/Diff-/Review-Gates ersetzen.

## Kanonische Dateien

- `fleet/repos.yml`: einzige normative Fleet-Mitgliedschaft.
- `automation/renovate/dependency-updates.v1.yml`: versionierte operative
  Rollout-Policy; keine zweite Fleet-Liste.
- `automation/renovate/default.json`: gemeinsamer Renovate-V1-Preset.
- `automation/renovate/expected-scope.v1.json`: deterministisch erzeugte,
  nicht-authoritative Scope-Projektion.
- `automation/renovate/baseline-2026-06-23_2026-07-23.json`: unveränderliche
  Vorher-Baseline für die Pilotbewertung.
- `scripts/fleet/renovate_policy.py`: fail-closed Validierung und Projektion.

Ein Consumer kann den zentralen Preset später beispielsweise über einen
Repo-gehosteten Preset-Pfad referenzieren. Der konkrete Consumer-Cutover ist
bewusst nicht Teil dieses Foundation-Tasks und benötigt eigene Repo-Claims,
Leases, Review- und Rollback-Evidenz.

## Single-Producer-Vertrag

Pro Repository und Dependency-Scope darf genau ein aktiver Produzent regulärer
Version-Update-PRs existieren.

Der Cutover ist daher strikt geordnet:

1. Renovate-Abdeckung im Zielrepo belegen.
2. Überlappende Dependabot-Version-Updates deaktivieren.
3. Per Readback bestätigen, dass nur ein Version-Update-Produzent aktiv ist.

`renovate_version_updates: prepared` bedeutet ausdrücklich **nicht aktiv**. Der
Foundation-Stand markiert alle geplanten Pilot-Repositories nur als `prepared`;
die erwartete aktive Hosted-App-Scope-Projektion ist deshalb leer.

Dependabot Security Updates bleiben in V1 als separater Security-Pfad bestehen.
Eine Version-Update-Migration behauptet nicht, Security Alerts oder
Security-Update-Verhalten zu deaktivieren oder zu ersetzen.

## Rollout-Wellen

1. `mitschreiber`: bestehende Custom-Pin-Erkennung modernisieren und ohne
   Automerge validieren.
2. `hausKI`, `hausKI-audio`: Volumenpilot gegen die 30-Tage-Baseline.
3. `repoground`: Signalqualität und Closed-unmerged-Verhalten untersuchen.
4. `weltgewebe`: Multi-Ecosystem-Pilot erst nach bestandenen früheren Wellen.
5. `metarepo`: Control-Plane-Cutover zuletzt, damit die Policy sich nicht selbst
   freigibt.
6. Restliche geeignete aktive Fleet-Repositories werden erst nach den Piloten
   bewertet; sie werden nicht als zweite vollständige Liste in der Policy
   dupliziert.

Zwischen automatischer Erweiterung zweier Wellen verlangt der Vertrag
mindestens zwei beobachtete Update-Zyklen. Die konkrete Freigabe bleibt an die
jeweiligen Repo-, Review-, CI- und Operator-Gates gebunden.

## Hosted-App-Scope

Für einen Mend-hosted Renovate-Pfad verlangt V1 GitHubs Auswahlmodus
`Select repositories`. Eine All-Repositories-Installation ist im V1-Vertrag
nicht zulässig.

`expected-scope.v1.json` enthält nur Repositories mit
`renovate_version_updates: enabled` als erwarteten aktiven App-Scope. Ein
beobachteter App-Scope kann mit `renovate_policy.py check --observed-app-scope`
gegen diese Git-autorisierte Erwartung geprüft werden. Eine Abweichung ist ein
fail-closed Driftbefund.

Die Projektion beweist weder, dass eine GitHub App installiert ist, noch dass
keine externe Installation existiert. Der tatsächliche GitHub-App-Zustand muss
live gelesen werden.

## Preset-Grenzen

Der gemeinsame Preset:

- erweitert `config:recommended`;
- setzt `automerge: false`;
- begrenzt PR-, Branch- und Stundenparallelität auf höchstens zwei;
- hält Major-Updates getrennt;
- gruppiert zentral nur Patch-/Minor-Updates für GitHub Actions; npm-/Cargo-Gruppen werden wegen Monorepo- und Verzeichnisgrenzen erst repo-spezifisch im jeweiligen Pilot definiert;
- enthält keine Post-Upgrade-Command-Ausführung.

Die lokale Validierung lehnt Automerge, gruppierte Major-Updates, zu hohe
Parallelität und unbekannte Policy-Felder fail-closed ab.

## Baseline und Messung

Die eingefrorene Vergleichsbasis vom 23. Juni bis 23. Juli 2026 enthält 51
Dependabot-PRs: 40 gemergt und 11 ohne Merge geschlossen. Die per Repository
gespeicherten Zähler werden beim Policy-Check gegen die reviewte Baseline
verifiziert.

Diese Zahlen beweisen weder eine Ursache für Merge-/Close-Entscheidungen noch
einen künftigen Vorteil von Renovate. Spätere Pilot-Auswertungen sollen unter
anderem PR-Zahl, Merge-Rate, Closed-unmerged-Anteil, stale PRs,
Duplicate-Producer-Vorfälle, Automerge-Vorfälle, Merge-Gate-Bypässe und echte
Bureau-Eskalationen vergleichen.

## Validierung

`just renovate-policy-check` prüft:

- Policy gegen die aktive Fleet aus `fleet/repos.yml`;
- keine archivierten oder `fleet: false` Repositories;
- keine Repo-Duplikate über Wellen;
- keine zwei gleichzeitig aktiven Version-Update-Produzenten;
- keinen vollständigen zweiten Fleet-Abzug in der Rollout-Policy;
- zentrale Preset-Sicherheitsgrenzen;
- unveränderte Baseline;
- bytegenaue Reproduzierbarkeit der Scope-Projektion.

`just renovate-policy` regeneriert ausschließlich die deterministische
Scope-Projektion. `just validate` führt den Check automatisch aus.

## Rollback

Dieser Foundation-Slice verändert keine Consumer-Dependabot-Konfiguration und
keine GitHub-App-Berechtigung. Er ist daher durch Revert des Metarepo-Commits
rückrollbar.

Jeder spätere Consumer-Cutover braucht zusätzlich einen eigenen Rollback:
Renovate für das betroffene Repository stoppen, den vorherigen reviewten
Dependabot-Version-Update-Stand wiederherstellen und anschließend live prüfen,
dass wieder exakt ein Version-Update-Produzent aktiv ist.

Bureau-, Chronik- und Git-Historie werden dabei nicht umgeschrieben.

## Bekannte Folgegrenze

`repo.mitschreiber` ist zum Stand dieser Entscheidung nicht als Bureau-
Repository-Resource registriert. T046 erfindet deshalb keinen Claim. Die
Resource-Katalog-Erweiterung und der Mitschreiber-Cutover müssen über den
operator-native Bureau-Intake als getrennte Folgearbeit registriert werden.
