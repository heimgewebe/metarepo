## Datenfluss: aussensensor → leitstand → heimlern

**MVP (heute):** `aussensensor` pusht an `leitstand` **und** direkt an `heimlern` (Skripte).
**Zielbild:** ingest **nur** via `leitstand`; `heimlern` konsumiert von dort (Stream/Webhook/Batch).

```mermaid
flowchart LR
 A[aussensensor] -- JSONL --> L[leitstand]
 L -- stream/batch --> H[heimlern]
 %% MVP-Workaround (direkt, zu entfernen)
 A -. direct (MVP) .-> H
```

**Migrationsnotiz:** Direktpfad ist **Übergang**. Neue Producer richten ingest ausschließlich auf `leitstand` aus.
