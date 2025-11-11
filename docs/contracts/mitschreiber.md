# Mitschreiber-Contracts (`os.context.*`)

Diese Contracts definieren das Austauschformat zwischen  
🪶 **mitschreiber** (OS-Kontext-Daemon) → **leitstand** → **semantAH** / **hausKI** / **heimlern**.  

Ziel: semantische Mitschriften – ohne Rohtext-Speicherung.

---

## 🎯 Leitprinzipien

| Prinzip | Bedeutung |
|----------|------------|
| **Offline-first** | Keine Cloud-Abhängigkeit. Alle Verarbeitung erfolgt lokal. |
| **Privacy-by-Design** | Nur Keyphrases + Embeddings verlassen den RAM. |
| **Consent-gesteuert** | Content-Aware-Mode ist immer ein aktives Opt-in. |
| **Audit-fähig** | leitstand protokolliert alle Annahmen, Ablehnungen und TTL-Löschungen. |

---

## 📦 Event-Klassen

### 1. `os.context.state`
> Laufende Statusmeldungen über App-/Fensterfokus und Aktivität.

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `ts` | string (date-time) | Zeitstempel |
| `app` | string | Applikations-Identifier (z. B. `code`, `obsidian`) |
| `window` | string | Fenster- oder Dokumenttitel |
| `focus` | boolean | true = Fenster im Vordergrund |
| `activity_rpm` | integer ≥ 0 | Tastatur/Maus-Aktivität pro Minute |

📄 Schema: [`contracts/os.context.state.schema.json`](../../contracts/os.context.state.schema.json)

---

### 2. `os.context.text.redacted`
> Flüchtige (nicht persistente) Ereignisse während der Text-Erfassung.  
> Dienen Debug- oder Audit-Zwecken im RAM/WAL-Modus (≤ 5 min TTL).

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `ts` | string (date-time) | Zeitpunkt der Erfassung |
| `app` | string | Herkunfts-App |
| `window` | string | Kontext-Fenster |
| `snippet` | string | redigierter Textabschnitt |
| `pii_detected` | string[] | erkannte PII- oder Secret-Typen |
| `confidence` | number | Erkennungs-Konfidenz |
| `privacy` | object | `{ "raw_retained": false }` usw. |

📄 Schema: [`contracts/os.context.text.redacted.schema.json`](../../contracts/os.context.text.redacted.schema.json)

---

### 3. `os.context.text.embed`
> Persistenter, privacy-sicherer Output (Embedding-Event).  
> Enthält semantische Repräsentationen, aber keinen Rohtext.

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `ts` | string (date-time) | Zeitpunkt der Extraktion |
| `app` | string | Ursprung |
| `window` | string | Fenster- oder Dokumentkontext |
| `keyphrases` | string[] | extrahierte Schlüsselbegriffe |
| `embedding` | number[] | numerischer Vektor (normiert, on-device berechnet) |
| `hash_id` | string | SHA-256 o. ä. für Dedup/Audit |
| `privacy` | object | `{ "raw_retained": false, "detector_ver": "v1.x" }` |

📄 Schema: [`contracts/os.context.text.embed.schema.json`](../../contracts/os.context.text.embed.schema.json)

---

## 🧰 Beispiel-Validierung (YAML Snippet)
Verwendung des Reusable-Workflows für JSONL-Validierung:

```yaml
jobs:
  validate:
    uses: heimgewebe/metarepo/.github/workflows/reusable-validate-jsonl.yml@contracts-v1
    with:
      jsonl_paths_list: |
        export/os/*.jsonl
        export/feeds/*.jsonl
      schema_url: https://raw.githubusercontent.com/heimgewebe/metarepo/contracts-v1/contracts/os.context.text.embed.schema.json
      strict: false
      validate_formats: true
```

---

## 🔒 Datenschutz-Richtlinien

1. **Kein Klartext** wird auf Datenträger geschrieben.
   Rohtexte existieren nur im RAM-Buffer (< 120 s) oder optional verschlüsselt im WAL (TTL ≤ 5 min).
2. **PII/Secret-Erkennung** erfolgt lokal (Regex + NER/ML).
   Funde oberhalb des `pii_gate.min_confidence` führen zu `drop_and_shred`.
3. **Allow/Block-Listen** werden vor der Erfassung geprüft.
   Gesperrte Apps/Domains → sofortiger Capture-Stopp + Audit-Event.
4. **Consent** muss durch `heimlern` erteilt sein (`user.consent.text_capture = true`).
5. **Audit-Trail** im `leitstand`:
   Jede Ablehnung (PII, Block, Rate-Limit) wird mit Grund und Hash vermerkt.

---

## 🧩 Ecosystem-Fluss

```
mitschreiber
 ├─ emits os.context.state            → leitstand
 ├─ emits os.context.text.embed       → leitstand
 │                                     ↓
 │                                semantAH.index
 │                                     ↓
 │                                hausKI  ⇄ heimlern
 └─ optional os.context.text.redacted (RAM/WAL only)
```

---

## 🧭 Versionierung

| Version | Tag            | Bemerkung                                        |
| ------- | -------------- | ------------------------------------------------ |
| v1      | `contracts-v1` | Einführung Mitschreiber-Contracts                |
| v2      | *in Planung*   | evtl. neue Felder (z. B. `session`, `workspace`) |

---

## 🧪 Tests

| Testziel         | Beschreibung                                                     |
| ---------------- | ---------------------------------------------------------------- |
| **PII-Canary**   | 100 Dummy-Secrets → ≥ 99 % erkannt u. verworfen                  |
| **Rate-Limit**   | > 12 Embeddings / min → Drop mit Audit                           |
| **Mode-Switch**  | metadata → content_aware → Pause → Resume ohne Leak              |
| **Schema-Drift** | Validation via `reusable-validate-jsonl.yml` besteht durchgehend |

---

## 🪶 Essenz

> **mitschreiber** ist kein Keylogger,
> sondern ein semantischer Gedächtnissensor.
> Er merkt sich Bedeutungen – nicht Wörter.

---

## ∴ Unsicherheits-Radar

| Bereich                       | Unsicherheitsgrad   | Ursache                                                     |
| ----------------------------- | ------------------- | ----------------------------------------------------------- |
| *Redaction-Recall*            | ⚙️ Mittel           | Regex + NER-Modell noch empirisch kalibriert                |
| *User-Consent-Handling*       | ⚙️ Niedrig          | Heimlern-Gate zuverlässig, aber UX-Abfrage noch zu testen   |
| *Embeddings-Leak-Risiko*      | ⚙️ Niedrig → Mittel | theoretisch rekonstruierbar bei sehr kleinen Modellen       |
| *Policy-Durchgriff (OS-Hook)* | ⚙️ Hoch             | Implementierungsabhängig (Plattform-API Verhalten variabel) |

---

## ∆-Radar

Die Einbindung des „mitschreiber“-Strangs markiert eine **Seitwärtsmutation** der Fleet-Architektur:

* weg von “Feed → Event” hin zu “Kontext → Bedeutung”;
* verstärkte lokale Semantik (semantAH rückt näher an den Client);
* Policies werden nicht nur konsumiert, sondern präventiv erzwingend.
  Trend: **produktive Verdichtung** statt Aufblähung – Funktion wächst,
  Struktur bleibt konzise.

```

