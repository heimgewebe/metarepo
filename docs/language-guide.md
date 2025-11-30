# Language Guide / Sprachleitfaden

This document explains the multilingual documentation strategy for the Heimgewebe metarepo.

## Documentation Languages

The Heimgewebe project uses a **pragmatic bilingual approach**:

### German (Deutsch) 🇩🇪
Primary language for:
- Core conceptual documentation (Konzepte, Leitlinien, Vision)
- Narrative documents and explanations
- Domain-specific terminology
- Files explicitly marked as German

**Examples:**
- `heimgewebe-gesamt.md`
- `konzept-kern.md`
- `leitlinien.md`
- `wgx-konzept.md`

### English 🇬🇧
Used for:
- Technical documentation (APIs, configurations)
- Tool documentation (actionlint, etc.)
- ADRs (Architecture Decision Records)
- International collaboration

**Examples:**
- `architecture.md`
- `contracts.md`
- ADR documents
- Tool documentation

## Why Bilingual?

1. **Authenticity**: Core concepts are developed in German, reflecting the natural thinking process
2. **Accessibility**: Technical documentation in English ensures international collaboration
3. **Pragmatism**: Use the most appropriate language for each document type

## Guidelines for Contributors

- **Respect the existing language** of a document
- German documents may contain English technical terms (e.g., "Template", "Drift", "Fleet")
- English documents may reference German concept names (e.g., "Heimgewebe", "hausKI")
- When creating new docs:
  - Conceptual/narrative → German preferred
  - Technical/API → English preferred
  - ADRs → English

## Translation Status

Not all documents require translation. We focus on:
- ✅ Key documents available in both languages (README sections)
- 📝 Language-specific documents clearly labeled
- 🔄 Cross-references work regardless of language

---

**See also:**
- [CONTRIBUTING.md](../CONTRIBUTING.md) – Contribution guidelines
- [docs/README.md](./README.md) – Documentation index
