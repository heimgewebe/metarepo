# Fleet-Quellen und `repos.yml`-Projektion

## Normative Quellen

Die Fleet ist **nicht** das vollständige Operator-Ökosystem und auch nicht die
Menge aller Repositories der Organisation.

- [`fleet/repos.yml`](../fleet/repos.yml) entscheidet ausschließlich über
  Fleet-Scope und Related-Einträge.
- [`fleet/repo-metadata.yml`](../fleet/repo-metadata.yml) enthält operative
  Zusatzdaten für bestehende Consumer, etwa Branch, Domain, Abhängigkeiten und
  Tooling-Overrides.
- [`repos.yml`](../repos.yml) ist eine generierte Kompatibilitätsprojektion und
  niemals eine Quelle für Mitgliedschaftsentscheidungen.

## Klassen

1. **Core-Fleet** – Einträge unter `repos:`. Sie gehören zur gemeinsam
   verwalteten Metarepo-Fleet und dürfen Ziel gemeinsamer Contracts, Templates,
   Workflows und Fleet-Prüfungen sein.
2. **Related** – Einträge unter `static.include` ohne `fleet: false`. Sie sind
   für Abdeckung oder Kompatibilität relevant, aber nicht automatisch
   Core-Fleet. Sie erscheinen nur dann in der Kompatibilitätsprojektion, wenn
   zusätzlich operative Metadaten vorhanden sind.
3. **Ausgeschlossen oder nur referenziert** – Einträge mit `fleet: false`.
   Sie dürfen weder in `repos.yml` projiziert noch allein aufgrund ihrer
   Erwähnung als Fleet-Ziel behandelt werden.

## Aufnahmekriterien

Ein Repository wird nur dann in `repos:` aufgenommen, wenn:

- ein konkreter gemeinsamer Contract-, Template-, Workflow- oder Prüfbedarf
  besteht;
- Name und Zuständigkeit eindeutig sind;
- Auswirkungen auf bestehende Consumer geprüft wurden;
- die Aufnahme nicht bloß eine allgemeine Zugehörigkeit zum Ökosystem
  ausdrücken soll.

Ein Related-Eintrag genügt, wenn ein Repository für Abdeckung oder Beziehungen
sichtbar sein muss, aber nicht als gemeinsam verwaltetes Ziel gelten soll.

## Projektion und Drift-Gate

```bash
just fleet-projection
just fleet-projection-check
```

`just fleet-projection` erzeugt `repos.yml` deterministisch aus beiden
normativen Fleet-Dateien. `just fleet-projection-check` und `just validate`
blockieren:

- manuelle Änderungen an `repos.yml`;
- Metadaten für unbekannte oder mit `fleet: false` ausgeschlossene Repositories;
- ungültige Abhängigkeiten oder Metadatenformen;
- eine vergessene Regeneration der Projektion.

Die vollständige Legacy-Semantik der Projektion ist zusätzlich durch einen
kanonischen SHA-256-Test gebunden. Änderungen daran sind daher bewusste
Consumer-Vertragsänderungen.

Die aktuelle gerenderte Mitgliedschaftsübersicht befindet sich unter
[`docs/_generated/fleet.md`](_generated/fleet.md).
