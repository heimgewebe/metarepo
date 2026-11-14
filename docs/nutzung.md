# Heimgewebe – Nutzung und täglicher Betrieb

Diese Seite ist eine **Orientierung, keine Live-Status- oder Steuerungsquelle**. Sie ersetzt die frühere Organismus-Anleitung mit nicht mehr gültigen WGX-Kommandos, Meta-Agenten und Rollenbildern. Ob eine Funktion gerade läuft, ergibt sich nur aus ihren Primärquellen.

## Wo finde ich die zuständige Funktion?

| Frage | Zuständige Quelle |
| --- | --- |
| Welche Systeme gibt es und wofür sind sie zuständig? | [Systemkatalog](https://github.com/heimgewebe/systemkatalog) |
| Welche Repositories gehören zur definierten Fleet? | [Metarepo `fleet/repos.yml`](../fleet/repos.yml) |
| Wo liegen gemeinsame Schemas, Vorlagen und CI-Workflows? | [Metarepo `contracts/`](../contracts/) und `.github/workflows/` |
| Was ist in Git, PRs, Reviews und CI tatsächlich passiert? | GitHub und die konkrete Repository-Revision |
| Welche Aufgaben sind reserviert, ausführbar oder abgeschlossen? | [Bureau](https://github.com/heimgewebe/bureau) |
| Wer führt lokale Änderungen, Service- und Diagnosearbeiten aus? | [Grabowski](https://github.com/heimgewebe/grabowski) |
| Wo finde ich frühere Reparaturen und Ereignisse? | [Chronik](https://github.com/heimgewebe/chronik), append-only, historische Evidenz |
| Wie erhalte ich reproduzierbaren Quellcodekontext für Agenten? | [RepoGround](https://github.com/heimgewebe/repoground), Bundles und Retrieval |
| Wie prüfe ich deklarierte Repository-Tasks? | [WGX](https://github.com/heimgewebe/wgx), lokaler Verifikationsrunner |
| Wo werden Ereignisse weitergeleitet? | [Plexer](https://github.com/heimgewebe/plexer), Ereignis-Gateway |
| Wo gibt es eine zusammengefasste Betriebsanzeige? | [Leitstand](https://github.com/heimgewebe/leitstand), read-only |
| Wo liegen semantischer Index und Wissensgraph? | [semantAH](https://github.com/heimgewebe/semantAH) |
| Wo liegt das eigenständige gesellschaftliche Produkt? | [commonThing](https://github.com/heimgewebe/commonthing) |

**Autoritätsgrenze:** Metarepo definiert Fleet-Mitgliedschaft und geteilte Verträge, aber weder die globale Systemarchitektur noch Aufgaben-/Deploy-Wahrheit. WGX koordiniert keine Fleet und besitzt keine generische Host- oder Ausführungsautorität.

## Typischer Ablauf

1. **Ziel abgrenzen:** Repository, Dienst oder konkreten Nutzerweg bestimmen.
2. **Historie lesen:** Bei Heimgewebe-Arbeit gezielt nach relevanten Chronik-Entscheidungen, Fehlschlägen und Reparaturen suchen.
3. **Gegenwart prüfen:** Exakten Git-Stand, offenen PR, CI, Leases, laufenden Dienst und gegebenenfalls echten Client durch ihre jeweiligen Primärquellen prüfen.
4. **Kleinste wirksame Änderung ausführen:** Repository-Validierung mit WGX; operative Host-, Checkout- und Serviceänderungen über Grabowski; Aufgaben-/Kollisionsabgleich über Bureau.
5. **Wirkung nachweisen:** Tests, aktualisierten Commit, PR-Status, tatsächliches Deployment, Laufzeitfunktion und bei riskanter Änderung Restore separat belegen.
6. **Ergebnis dokumentieren:** Relevante Erkenntnisse und bestätigte Fehlerursachen mit Quellen in der Chronik festhalten. Nicht aus dem Merge allein auf Produktnutzen schließen.

## WGX – tatsächlich unterstützte Befehle

WGX liest die `.wgx/profile.yml` des **ausgewählten Ziel-Repositories**. Es besitzt nur drei operative Einstiegspunkte:

```bash
wgx validate --profile quick
wgx validate --profile full
wgx tasks
wgx task smoke
```

`smoke` ist dabei nur ein Beispiel: Der Name muss im jeweiligen Repository-Profil deklariert sein. Es gibt **keine** allgemeinen WGX-Unterbefehle `wgx guard`, `wgx metrics snapshot` oder `wgx bridge` als heutige Produkt-API. Für gemeinsame CI-Workflows gelten die im Metarepo tatsächlich versionierten Dateien, nicht historische Beispielnamen.

## Repository in die Fleet aufnehmen

Die Mitgliedschaft wird in [`fleet/repos.yml`](../fleet/repos.yml) gepflegt. Das neue Repository versieht seine fachlichen Verträge, benötigten Tests und gegebenenfalls sein WGX-Verifikationsprofil selbst mit Versionen. Gemeinsame Schemas und Reusable Workflows werden über Metarepo bezogen. Ein Eintrag im Fleet-Vertrag sagt nichts über einen aktuell gesunden Dienst oder eine erledigte Aufgabe aus.

## Abgelöste Komponenten

Die früheren Repositories **HausKI, hausKI-audio, Heimgeist, Sichter, Heimlern, Aussensensor, Mitschreiber und Vault-Gewebe** sind keine aktuellen operativen Fleet-Organe. Der frühere Produktname **Lenskit / repoLens / rLens** wurde durch RepoGround ersetzt. Persistierte Schema-IDs, historische Dokumente und unveränderliche Ereignisse dürfen alte Namen weiterhin enthalten, solange die Kompatibilität oder Provenienz sie erfordert.

Ältere detaillierte Anleitungen bleiben in der Git-Historie dieser Datei nachvollziehbar. Vor jeder Übernahme historischer Befehle ist die tatsächlich vorhandene CLI und die zuständige Primärquelle zu prüfen.
