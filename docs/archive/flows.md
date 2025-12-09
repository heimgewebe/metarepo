## Datenfluss: aussensensor → chronik → heimlern

**MVP (heute):** `aussensensor` pusht an `chronik` **und** direkt an `heimlern` (Skripte).
**Zielbild:** ingest **nur** via `chronik`; `heimlern` konsumiert von dort (Stream/Webhook/Batch).

```mermaid
flowchart LR
 A[aussensensor] -- JSONL --> C[chronik]
 C -- stream/batch --> H[heimlern]
 %% MVP-Workaround (direkt, zu entfernen)
 A -. direct (MVP) .-> H
```

**Migrationsnotiz:** Direktpfad ist **Übergang**. Neue Producer richten ingest ausschließlich auf `chronik` aus.
