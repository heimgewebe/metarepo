# Fleet-Operations im Metarepo

Das Metarepo verwaltet gemeinsame Fleet-Assets für **explizit aufgenommene**
Repositories. Es ist weder Leitstelle für alle Repositories unter `heimgewebe`
noch Quelle der gesamten Ökosystemarchitektur.

Die Quellen sind getrennt:

- `fleet/repos.yml` – normative Fleet-Mitgliedschaft und Related-Scope;
- `fleet/repo-metadata.yml` – operative Zusatzdaten für bestehende Consumer;
- `repos.yml` – deterministisch generierte, nicht normative
  Kompatibilitätsprojektion.

Die kanonische WGX-Dokumentation bleibt im
[WGX-Repository](https://github.com/heimgewebe/wgx).

## Verantwortungsabgrenzung

- **Metarepo**
  - kuratiert Fleet-Scope und Standard-Templates unter `templates/**`;
  - pflegt wiederverwendbare Workflows und Runbooks;
  - erzeugt die Kompatibilitätsprojektion für noch nicht migrierte Consumer;
  - initiiert Fleet-Zyklen über `just` oder `scripts/wgx`.
- **WGX-Repository**
  - enthält Master-Dokumentation, Policies und Guard-Implementierung;
  - liefert die ausführbare Engine; das Metarepo ruft sie nur auf.
- **Systemkatalog**
  - beschreibt das vollständige Operator-Ökosystem und seine Beziehungen;
  - leitet daraus keine Metarepo-Fleet-Mitgliedschaft ab.

## Fleet-Änderung

1. Mitgliedschaft ausschließlich in `fleet/repos.yml` ändern.
2. Nur benötigte operative Daten in `fleet/repo-metadata.yml` ergänzen.
3. `just fleet-projection` ausführen.
4. `just fleet-projection-check` und `just validate` ausführen.
5. Auswirkungen auf WGX-, Graph-, Template- und Integrity-Consumer prüfen.

`repos.yml` darf nicht manuell bearbeitet werden. Einträge mit `fleet: false`
sind nicht projektierbar und dürfen nicht allein aufgrund ihrer Erwähnung als
Fleet-Ziel behandelt werden.

## Fleet-Zyklus: sync → validate → smoke

1. **sync** – `just up` oder `./scripts/wgx up`
   - spiegelt Templates und Runbooks in die ausgewählten Ziel-Repositories;
   - nutzt `templates/**` als jeweilige Asset-Quelle.
2. **validate** – `just wgx:validate` oder `./scripts/wgx validate`
   - prüft die generierte `repos.yml`-Kompatibilitätsfläche und die erwarteten
     Templates;
   - `just validate` prüft zusätzlich Projektionsdrift, YAML, Tests und
     Workflow-Linting.
3. **smoke** – `just smoke` oder `./scripts/wgx smoke`
   - startet die vorgesehenen WGX-Smoke-Workflows;
   - das Ergebnis ist ein technischer Prüfbefund, keine allgemeine
     Ökosystemgesundheit.

## Betriebsnotizen

- `reports/` enthält nicht normative Drift- und Doctor-Ausgaben.
- Fleet-Aufnahmen und -Entfernungen benötigen eine begründete Consumerprüfung.
- Für Ad-hoc-Syncs einzelner Repositories gilt weiterhin
  `scripts/sync-templates.sh --push-to <repo> --pattern "templates/**"`.

## Siehe auch

- [Fleet-Quellen und Projektion](../repos.yml.md)
- [WGX-Konzept](./wgx-konzept.md)
- [Templates](../templates.md)
- [Push to Fleet](./push-to-fleet.md)
- [ADR-0002: Fleet-Rollout via reusable GitHub Actions](../adrs/0002-reusable-actions-rollout.md)
