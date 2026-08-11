# Auflösung kanonischer Contractquellen

Konsumenten des Heimgewebes validieren gegen die von Metarepo veröffentlichten
Contractbytes. Dieses Dokument legt fest, **woher** diese Bytes stammen dürfen und
**wie** die Herkunft belegt wird. Es beschreibt keine semantische Gültigkeit,
keine Live-Nutzung und keine Merge-Reife.

## Auflösungsreihenfolge

Eine Auflösung ist gültig, wenn genau eine Quelle explizit benannt wurde:

1. **Expliziter Git-Checkout** — der Konsument bekommt den Repositorywurzelpfad
   als Argument. Die Quelle wird über `remote.origin.url` gegen
   `heimgewebe/metarepo` geprüft, der 40-stellige `HEAD` wird festgehalten, ein
   unsauberer Baum schlägt fehl.
2. **Unveränderliche, manifestgebundene Quelle** — ein losgelöstes Archiv oder ein
   freigegebener Offline-Cache, gebunden durch ein
   `contract.source.manifest.schema.json`-Manifest.

Ein danebenliegendes Verzeichnis, eine Umgebungsvariable oder ein bestimmter
Ausführungswrapper sind **nie** stille Autorität. Fehlt die explizite Angabe,
schlägt die Validierung fehl; sie fällt nicht auf einen Suchpfad zurück.

Weil sämtliche Eingaben Kommandozeilenargumente sind, überstehen synchrone wie
dauerhafte Ausführungswege (Shell, CI-Step, Grabowski-Route) die Auflösung
unverändert: es gibt keine verdeckte Shell-Initialisierung, die erhalten werden
müsste, und ein weggelassenes Argument wird typisiert abgelehnt statt geraten.

## Manifest erzeugen

`scripts/contracts/emit_source_manifest.py` ist der reproduzierbare Produzent.
Er liest ausschließlich aus einem explizit benannten, identitätsgeprüften und
sauberen Metarepo-Checkout. Auswahl und Bytes kommen aus dem festgehaltenen
`HEAD`-Tree und seinen Git-Blobs, nicht aus Arbeitsbaumdateien:

```bash
python3 scripts/contracts/emit_source_manifest.py \
  --source /pfad/zum/metarepo \
  --out-dir /pfad/zum/archiv \
  --consumer heim-pc \
  --source-kind detached_archive \
  --expected-commit 0123456789abcdef0123456789abcdef01234567
```

Ergebnis ist `metarepo-contract-source.v1.json` neben einer Inhaltswurzel
(`content/` per Vorgabe) mit exakt den gebundenen Schemabytes.

- `--consumer NAME` bindet jedes in `HEAD` getrackte Schema unter
  `contracts/NAME/`.
- `--schema PFAD` bindet ein einzelnes Schema zusätzlich.
- Für jede Auswahl wird die transitive Closure lokaler relativer `$ref`s
  gebunden. Fragment-only-Refs bleiben im selben Blob; normalisierte
  Cross-Namespace-Refs unter `contracts/` werden verfolgt; Zyklen sind erlaubt.
  Fehlende, ungültige oder aus `contracts/` escapende lokale Ziele brechen
  typisiert ab. URIs mit Scheme oder Authority bleiben externe Referenzen und
  werden niemals über ihren URI-Pfad als lokale Dateien interpretiert.
- Ohne `--consumer`/`--schema` bricht der Lauf ab; ein Manifest ohne Bindung ist
  wertlos.
- Ein unsauberer Quellbaum bricht ab: ein Manifest behauptet unveränderliche
  Bytes.
- Ignorierte, ausgeschlossene, ungetrackte oder nur im Arbeitsbaum vorhandene
  Schemas sind keine Bytes des gebundenen Commits und werden niemals attestiert.
- Das Ausgabeverzeichnis darf nicht innerhalb der Quelle liegen und ein
  vorhandener, nicht leerer Inhaltsbaum wird nur mit `--overwrite` ersetzt.

Die Ausgabe ist deterministisch: gleiche Quelle und gleiche Auswahl ergeben
byteidentische Manifeste. Zeitstempel und maschinenlokale Pfade sind nicht Teil
des Manifests.

## Cache prüfen

`--verify` schreibt nichts, sondern belegt, dass ein vorhandenes Manifest und
sein Inhaltsbaum weiterhin exakt der gebundenen Quelle entsprechen:

```bash
python3 scripts/contracts/emit_source_manifest.py \
  --source /pfad/zum/metarepo \
  --out-dir /pfad/zum/cache \
  --consumer heim-pc \
  --source-kind offline_cache \
  --verify
```

Abweichendes Manifest, veränderte, fehlende oder ungebundene Dateien im Cache
werden mit typisiertem Fehler abgelehnt.

## Typisierte Fehler

Jeder Provenienz-, Auswahl-, Materialisierungs- oder Prüffehler nach erfolgreicher
CLI-Syntaxprüfung ist ein stabiler Code auf `stderr`, Exitcode `2`. Syntaxfehler
meldet `argparse` ebenfalls mit Exitcode `2`. Ein Fehlschlag kann nicht als Erfolg
missverstanden werden, weil im Erfolgsfall das gerenderte Manifest auf `stdout`
erscheint und Exitcode `0` gilt.

| Code | Bedeutung |
| --- | --- |
| `SOURCE_MISSING`, `SOURCE_NOT_GIT`, `SOURCE_NOT_REPOSITORY_ROOT` | Die benannte Quelle ist kein auflösbarer Git-Repositorywurzelpfad. |
| `SOURCE_WRONG_REPOSITORY` | `remote.origin.url` löst nicht auf `heimgewebe/metarepo` auf. |
| `SOURCE_COMMIT_INVALID`, `SOURCE_COMMIT_MISMATCH`, `EXPECTED_COMMIT_INVALID` | Commitbindung fehlt oder weicht ab. |
| `SOURCE_DIRTY` | Der Quellbaum trägt verfolgte oder nicht ignorierte ungetrackte Änderungen. |
| `SCHEMA_SELECTION`, `CONSUMER_UNKNOWN`, `CONSUMER_EMPTY`, `CONSUMER_INVALID` | Die Auswahl bindet nichts oder benennt keinen vorhandenen Namensraum. |
| `SOURCE_KIND_INVALID`, `CONTENT_ROOT_INVALID` | Quellenart oder relativer Inhaltswurzelpfad ist unzulässig. |
| `SCHEMA_PATH_INVALID`, `SCHEMA_PATH_ESCAPE`, `SCHEMA_NOT_TRACKED`, `SCHEMA_NOT_REGULAR`, `SCHEMA_UNREADABLE` | Eine Auswahl ist nicht kanonisch, nicht im gebundenen Commit getrackt, kein regulärer Git-Blob oder nicht lesbar. |
| `SCHEMA_JSON_INVALID`, `SCHEMA_REF_INVALID`, `SCHEMA_REF_ESCAPE`, `SCHEMA_REF_MISSING` | Eine lokale `$ref`-Closure kann nicht vollständig und sicher aus den gebundenen Git-Blobs gebildet werden. |
| `OUT_DIR_INSIDE_SOURCE`, `OUT_DIR_MISSING`, `OUT_DIR_INVALID`, `OUT_DIR_UNWRITABLE`, `CONTENT_ROOT_NOT_EMPTY` | Das Ausgabeziel ist unzulässig oder würde bestehenden Inhalt still ersetzen. |
| `CONTENT_ROOT_MISSING`, `CONTENT_ROOT_INVALID_TYPE`, `CONTENT_ROOT_PATH_ESCAPE` | Die Inhaltswurzel fehlt, ist kein Verzeichnis oder traversiert einen Symlink. |
| `MANIFEST_MISSING`, `MANIFEST_UNREADABLE`, `MANIFEST_INVALID_TYPE`, `MANIFEST_DRIFT` | Prüfung gegen ein fehlendes, nicht reguläres, unlesbares oder abweichendes Manifest. |
| `CONTENT_MISSING`, `CONTENT_UNREADABLE`, `CONTENT_INVALID_TYPE`, `CONTENT_DRIFT`, `CONTENT_UNBOUND` | Der Cache fehlt, enthält nicht reguläre Knoten oder weicht von den gebundenen Bytes ab. |

## Konsumentenpflichten

Ein Konsument, der eine manifestgebundene Quelle verwendet, muss

- jedes verwendete Schema im Manifest wiederfinden und den SHA-256 vor der
  Nutzung prüfen,
- die Inhaltswurzel nicht verlassen,
- Repositoryidentität und Commit in seinen Validierungsbeleg übernehmen,
- und bei fehlender, abweichender oder ungebundener Quelle fail-closed abbrechen.

`heim-pc` setzt genau das in `scripts/contract_source.py` um und schreibt einen
deterministischen Validierungsbeleg mit Quellidentität, Commit, Dirty-State,
Schemapfaden samt SHA-256, Konsumenten-`HEAD` und Artefakt-Hashes.
