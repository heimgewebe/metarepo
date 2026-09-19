# Historische Contract-Referenz: `os.context.*` (mitschreiber)

> **Status:** historisch. Das Repository `heimgewebe/mitschreiber` wurde am 2026-09-18 physisch gelöscht und ist kein aktueller Producer, Daemon oder Fleet-Teilnehmer.

Dieses Dokument beschreibt die frühere Mitschreiber-Kopplung als Provenienz. Die `os.context.*`-Schemas bleiben im Metarepo als Datenverträge erhalten. Aktuelle Producer-/Consumer-Claims werden ausschließlich aus `contracts/consumers.yaml` und `contracts/consumer-evidence.v1.json` abgeleitet.

## Historischer Datenfluss

Früher: `mitschreiber` → `chronik` → semantische Consumer. Dieser Pfad belegt **keine aktuelle Eventquelle**.

Die Contractfamilie umfasst unter anderem `os.context.intent`, `os.context.state`, `os.context.text.embed` und `os.context.text.redacted`.

## Historische Sicherheitsannahmen

Die frühere OS-Kontext-Erfassung war hochsensibel. Aussagen über lokale Erfassung, Redaction, TTL oder Export in älteren Mitschreiber-Dokumenten sind historische Implementierungsannahmen und keine Zusage über einen heutigen Producer.

## Nutzung heute

- **Historische Lernreferenz:** frühere Heimlern-Kopplungen bleiben ausschließlich als historische Contract-Evidenz nachvollziehbar und begründen keinen aktuellen Consumer.
- Schema-Bytes aus `contracts/` können weiterhin zum Dekodieren oder Validieren vorhandener Daten verwendet werden.
- Ein neuer Producer muss separat registriert und evidence-bound verifiziert werden.
- Aus dem Namen `mitschreiber` darf kein aktueller Service, Prozess, Endpoint oder Repository-Pfad abgeleitet werden.
