# Kernkonzepte des Metarepo

Das Metarepo veröffentlicht gemeinsame Fleet-Assets für ausdrücklich
aufgenommene Repositories. Seine normative Rolle ist in
[`system/metarepo-role.v1.json`](../system/metarepo-role.v1.json) festgelegt.
Es ist keine Control Plane und keine Quelle der gesamten
Ökosystemarchitektur.

## Kernflächen

- **`fleet/repos.yml`** – einzige normative Quelle der Fleet-Mitgliedschaft und
  des Related-Scope.
- **`fleet/repo-metadata.yml`** – operative Zusatzdaten für bestehende
  Metarepo-Consumer, beispielsweise Branch, Domain, Abhängigkeiten und
  Tooling-Overrides.
- **`repos.yml`** – deterministisch erzeugte, nicht normative
  Kompatibilitätsprojektion für noch nicht migrierte WGX-, Graph-, Readiness-
  und Template-Consumer.
- **`templates/`** – kuratierte Vorlagen, die ausdrücklich für mehrere
  Consumer-Repositories bestimmt sind.
- **`.github/workflows/`** – wiederverwendbare CI-Bausteine und ihre
  Kompatibilitätsverträge.
- **`contracts/`** – gemeinsame versionierte Daten- und Workflowverträge.

## Wahrheitsgrenzen

Fleet-Mitgliedschaft bedeutet nicht automatisch Zugehörigkeit zum gesamten
Operator-Ökosystem. Systemzwecke und Beziehungen gehören in den Systemkatalog;
Aufgabenstatus und Abschlusswahrheit ins Bureau; operative Ausführung,
Leases und Recovery zu Grabowski.

Ein Repository wird nur dann in die Core-Fleet aufgenommen, wenn ein konkreter
gemeinsamer Contract-, Template-, Workflow- oder Prüfbedarf besteht.
`static.include` kann Related-Repositories sichtbar machen. Einträge mit
`fleet: false` sind nicht projektierbar und dürfen nicht als Fleet-Ziel
behandelt werden.

## Projektion statt zweiter Wahrheit

Die operative Legacy-Struktur bleibt vorübergehend erhalten, wird aber nicht
mehr manuell gepflegt:

```bash
just fleet-projection
just fleet-projection-check
```

Der Generator liest ausschließlich `fleet/repos.yml` und
`fleet/repo-metadata.yml`. `just validate` prüft bytegenaue Reproduzierbarkeit.
Die semantische Struktur der Projektion ist zusätzlich an einen
Consumer-Vertragstest gebunden.

## Verteilung gemeinsamer Assets

### Metarepo → Consumer

Kuratierte Templates, Contracts oder reusable Workflows werden nach
Consumerprüfung veröffentlicht. Bestehendes WGX- oder Sync-Tooling kann die
generierte `repos.yml` weiterverwenden, bis es auf die kanonischen Quellen
umgestellt ist.

### Consumer → Metarepo

Verbesserungen aus einzelnen Repositories werden nicht automatisch zur
Fleet-Norm. Sie müssen im Metarepo kuratiert, gegen aktive Consumer geprüft und
als eigener Review- und Mergevorgang veröffentlicht werden.

### Drift

Drift bezeichnet eine Abweichung zwischen normativen Quellen, generierten
Projektionen oder verteilten gemeinsamen Assets. Driftberichte sind Befunde;
sie ändern weder Fleet-Mitgliedschaft noch Aufgabenstatus automatisch.

## Siehe auch

- [Fleet-Quellen und `repos.yml`-Projektion](./repos.yml.md)
- [Fleet-Operations](./fleet/fleet.md)
- [Templates](./templates.md)
- [WGX-Konzept](./fleet/wgx-konzept.md)
- [ADR-002: Distribution und Drift](./adrs/002-distribution-drift.md)
