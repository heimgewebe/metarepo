# Integrity Strictness – Semantik, Storage, Transport

## Zweck dieses Dokuments

Dieses Dokument beendet die wiederkehrende Diskussion um „strict vs. tolerant“ im Integrity-Loop.
Es trennt **bewusst und explizit** drei Ebenen, die häufig vermischt werden:

1. **Semantik (Wahrheitslogik)**
2. **Storage (Persistenz & Schema)**
3. **Transport (Events & Benachrichtigung)**

Jede Ebene folgt eigenen Regeln.
Verstöße entstehen fast immer dort, wo diese Ebenen implizit vermengt werden.

---

## 1. Strict Semantics (nicht verhandelbar)

**Definition:**
„Strict“ bezieht sich ausschließlich auf die **semantische Bewertung des Zustands**, nicht auf Transport oder Persistenz.

### Semantische Invarianten

Ein Integrity-Report ist **semantisch FAIL**, wenn mindestens eines gilt:

- `generated_at` fehlt
- `generated_at` ist nicht ISO-8601-parsebar
- `generated_at` liegt signifikant in der Zukunft (> definierter Toleranz)
- `repo` fehlt oder ist nicht eindeutig identifizierbar
- `status` liegt außerhalb des erlaubten Enums

➡️ **Strict heißt:**
> Ungültige Wahrheit bleibt ungültig.
> Sie darf nicht zu OK, WARN oder „still akzeptiert“ werden.

---

## 2. Schema-valider Storage (notwendig, aber ehrlich)

**Problem:**
Persistenzsysteme (Chronik) benötigen **parsebare, schema-valide Daten**, selbst wenn diese semantisch defekt sind.

**Lösung:**
Sanitization ist erlaubt – aber **niemals unsichtbar**.

### Storage-Regeln

- Wenn `generated_at` fehlt oder ungültig ist:
  - `status` wird **FAIL**
  - `generated_at` wird auf `received_at` normalisiert
  - **Pflichtfeld:**
    ```json
    "generated_at_sanitized": true
    ```

- Wenn `generated_at` gültig ist:
  - Wert bleibt unverändert
  - `generated_at_sanitized` **darf nicht existieren**

➡️ **Wichtig:**
Sanitization dient **nur** der technischen Persistenz.
Sie **heilt keine Semantik**.

> _Sanitization is not healing._

---

## 3. Best-Effort Transport (absichtlich schwach)

**Grundsatz:**
Integrity ist **Pull-first**.

- **Source of Truth:**
  `summary.json` als Release-Asset (`/releases/download/integrity/summary.json`)
- **Events (`integrity.summary.published.v1`) sind:**
  - Hinweise
  - Trigger
  - Optimierungen
  - **niemals Wahrheitsträger**

### Transport-Regeln

- Event-Verlust, HTTP-Fehler oder Token-Probleme:
  - **dürfen den Integrity-Loop nicht brechen**
- Transportfehler:
  - werden als `WARN` geloggt
  - **niemals** als Systemfehler eskaliert

➡️ **Best-Effort heißt:**
> Transport darf scheitern, ohne Bedeutung zu erzeugen.

---

## 4. Entscheidungsdiagramm (kanonisch)

```
        ┌───────────────┐
        │ Report kommt  │
        └───────┬───────┘
                │
      ┌─────────▼─────────┐
      │ Semantik valide?   │
      │ (repo, status, ts) │
      └───────┬─────┬─────┘
              │     │
            JA│     │NEIN
              │     │
  ┌───────────▼┐   ▼────────────────────┐
  │ Status OK / │   │ Status = FAIL      │
  │ WARN / etc. │   │ (strict)           │
  └───────┬────┘   └─────────┬──────────┘
          │                  │
          │        ┌─────────▼─────────┐
          │        │ Storage braucht   │
          │        │ gültiges Schema   │
          │        └─────────┬─────────┘
          │                  │
          │        ┌─────────▼──────────────┐
          │        │ generated_at =         │
          │        │ received_at            │
          │        │ + sanitized flag       │
          │        └─────────┬──────────────┘
          │                  │
  ┌───────▼──────────────────▼───────────┐
  │ Persistieren (Chronik)                │
  └──────────────────────────────────────┘

  Event-Versand (optional, best-effort)
  ↓
  Fehler → WARN, niemals FAIL
```

---

## 5. Typische Fehlannahmen (explizit verworfen)

- ❌ „Sanitized Timestamp macht den Report wieder brauchbar“
- ❌ „Event = Wahrheit“
- ❌ „Strict heißt: alles ablehnen“
- ❌ „Fehlender Transport ist ein Fehler im Integrity-System“

---

## Verdichtete Essenz

> **Strict in der Bedeutung.
> Tolerant in der Technik.
> Gleichgültig im Transport.**

Wer diese drei Ebenen trennt, bekommt ein stabiles System.
Wer sie vermischt, bekommt endlose Debatten.

---

## Ungewissheitsanalyse

**Unsicherheitsgrad:** niedrig–mittel (≈ 0.2)

**Ursachen der Ungewissheit:**
- Zeitgrenzen („future timestamp“) sind konfigurationsabhängig
- Semantische Grenzfälle (UNCLEAR vs. WARN) bleiben interpretationsoffen
- Menschliche Fehlinterpretation der Flag-Bedeutung möglich

**Bewertung:**
Die Unsicherheit ist **produktiv**:
Sie bleibt sichtbar, statt durch falsche Striktheit verdeckt zu werden.

---

## Leitfragen (Selbstprüfung)

1. Wird hier irgendwo Sanitization mit Wahrheit verwechselt?
2. Würde ein verlorenes Event heute noch Diskussionen auslösen?
3. Ist klar erkennbar, **warum** ein Report FAIL ist – auch wenn er gespeichert wurde?

Wenn alle drei mit „Nein“ beantwortet werden:
Dieses Dokument hat seinen Zweck erfüllt.
