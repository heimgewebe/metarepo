# ADR-0022 Erkenntnis-Vorlauf & Negationsspur als Systemprinzip

Status: Proposed
Datum: 2025-12-14
Kontext: Heimgewebe-Organismus (Events, Semantik, Entscheidungen, Lernen)
Betroffene Achsen: Semantik (semantAH), Entscheidungen (hausKI), Lernen (heimlern), Chronik (chronik)

---

## 1. Kontext & Problemstellung

Heimgewebe verarbeitet Ereignisse, erzeugt semantische Verdichtungen (Insights) und trifft darauf basierend Entscheidungen (hausKI), die Lernprozesse (heimlern) auslösen.

Beobachtetes Problem:

- Entscheidungen erscheinen im System primär als Resultate, nicht als erkenntnisgeschichtliche Prozesse.
- Widerspruch, Unsicherheit und nicht-gewählte Alternativen sind implizit, verstreut oder verloren.
- Das System tendiert zur Verdichtung von Sinn, nicht zur Sichtbarmachung von Spannung.

Risiken:

- Entscheidungen wirken ex post „alternativlos“.
- Lernen erfolgt überwiegend aus Bestätigung, weniger aus Irrtum.
- Spätere Systemanalysen rekonstruieren was entschieden wurde, aber nicht warum andere Wege verworfen wurden.

---

## 2. Entscheidung

Heimgewebe führt zwei systemische Prinzipien ein.

### 2.1 Erkenntnis-Vorlauf vor Entscheidungen

Vor jeder wirksamen Entscheidung wird ein expliziter Erkenntnis-Vorlauf erzeugt und persistiert.

Neues Event:

- `decision.preimage`

`decision.preimage` ist ein forensischer Snapshot des Erkenntnisstands unmittelbar vor einer Entscheidung.
Er ist kein Entwurf, kein Abstimmungsartefakt und kein Planungsobjekt.

Enthält u. a.:

- Ausgangslage (relevante Insights, Events)
- erkannte Alternativen (mindestens 1)
- Unsicherheiten inkl. Ursachen (Datenlücke, Ambiguität, Modellannahme)
- Gewichtungen (explizit oder implizit)
- offene Fragen, die nicht aufgelöst wurden

Die eigentliche Entscheidung referenziert diesen Vorlauf.

---

### 2.2 Negationsspur als First-Class-Signal

Widerspruch wird nicht als Fehler oder Sonderfall behandelt, sondern als produktives Systemereignis.

Neue semantische Struktur:

- `insight.negation`

`insight.negation` ist keine Meinungsäußerung, sondern eine strukturierte Gegeninterpretation mit epistemischem Bezug.

Eigenschaften:

- Jede starke These kann eine Negation erzeugen (automatisch oder manuell).
- Negationen sind keine Blockaden, sondern alternative Deutungsräume.
- Negationen werden nicht „aufgelöst“, sondern mitgeführt.

Negationen können entstehen durch:

- semantAH (automatische Gegenthese)
- Nutzerfeedback
- spätere Ereignisse
- externe Signale (z. B. Gegenargumente aus Streams)

---

## 3. Konsequenzen für die Architektur

### 3.1 semantAH

- erzeugt nicht nur verdichtete Knoten, sondern auch Kontrastknoten
- markiert Unsicherheitsursachen explizit
- unterstützt relationale Paare: these ⟂ antithese

### 3.2 hausKI

- trifft Entscheidungen nicht ohne preimage
- kann Entscheidungen bewusst trotz hoher Unsicherheit treffen (aber sichtbar)
- kann Negationen ignorieren, muss dies aber begründen

### 3.3 heimlern

- lernt nicht nur aus Erfolg/Misserfolg
- lernt explizit aus:
  - verworfenen Alternativen
  - später bestätigten Negationen
  - systematischen Fehleinschätzungen

### 3.4 chronik

- speichert nicht nur Fakten, sondern Entscheidungs-Kontexte
- ermöglicht retrospektive Analysen:
  - „Wo lag das System falsch?“
  - „Welche Unsicherheit wurde unterschätzt?“

---

## 4. Abgrenzung

Bewusst nicht Teil dieser ADR:

- keine metaphysische „Wahrheitssphäre“
- keine moralische Bewertung von Entscheidungen
- keine Verpflichtung, Negationen aufzulösen
- kein UI-Dogma (Darstellung ist nachgelagert)

Heimgewebe bleibt technisch, nüchtern, operativ.

---

## 5. Vorteile

- höhere Auditierbarkeit von Entscheidungen
- robustere Lernprozesse
- Reduktion von Selbstbestätigungsdynamiken
- bessere Erklärbarkeit gegenüber Menschen
- langfristig höhere Systemvertrauenswürdigkeit

---

## 6. Risiken & Gegenmaßnahmen

Risiko: Überkomplexität
→ Gegenmaßnahme: Negationen optional, Schwellenwerte für automatische Erzeugung

Risiko: Entscheidungsparalyse
→ Gegenmaßnahme: Entscheidung trotz Unsicherheit explizit erlauben

Risiko: Überinterpretation von Subtext
→ Gegenmaßnahme: Subtext-Signale stets als weich, nie als harte Wahrheit markieren

---

## 7. Status & nächste Schritte

- Diskussion im Metarepo
- prototypische Umsetzung:
  - `decision.preimage` Event
  - einfache `insight.negation` Struktur
- Beobachtung realer Systemeffekte
- iterative Verfeinerung

---

## 8. Verdichtete Essenz

Heimgewebe entscheidet nicht nur –
es zeigt, wie es hätte anders entscheiden können.
