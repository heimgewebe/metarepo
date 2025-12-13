# Heimgewebe – Projektordner (Meta-Ebene)

Dieser Ordner ist die zentrale Meta-Dokumentation für den Heimgewebe-Organismus.

Er dient als:
- Orientierungsanker für KI-Agenten,
- Driftbremse für Architektur-Entscheidungen,
- Sammelpunkt für Overviews, Dumps, Roadmaps und Playbooks.

## Grundidee

Heimgewebe ist ein verteilter technischer Organismus.
Er besteht aus spezialisierten Repositories, die über Events, Semantik,
Entscheidungen und Motorik miteinander verbunden sind.

Dieser Ordner beschreibt nicht einzelne Repos,
sondern das Zusammenspiel des Gesamtsystems.

## Zentrale Achsen des Organismus

- Events / Chronik
  Alles Relevante wird als Event sichtbar (z. B. `event.line`, `aussen.event.*`).

- Semantik / Wissen
  `semantAH` erzeugt Bedeutung (Insights, Graph, Embeddings).

- Entscheidungen
  `hausKI` orchestriert, trifft Entscheidungen und verbindet Achsen.

- Fleet / Motorik
  `wgx` standardisiert Guard, Smoke, Metriken und Fleet-Health.

- Commands
  Intentionen entstehen primär über Git/CI, strikt getrennt von Events.

- OS-Kontext
  `mitschreiber` erfasst Fenster, Apps, Texte als `os.context.*`.

## Nutzungsregeln für KI-Agenten

1. Contracts first
   Keine Annahmen treffen, bevor Dumps, Contracts und Zielbilder gelesen wurden.

2. Events ≠ Commands
   Ereignisse sind Fakten, Commands sind Absichten. Nicht vermischen.

3. WGX bevorzugen
   Für CI, Guard, Smoke, Metriken ist `wgx` die Standard-Motorik.

4. Keine Halluzination
   Fehlende Information explizit als Lücke markieren, nicht auffüllen.

5. Jede Empfehlung prüfen
   - Prämissencheck
   - Risikoabschätzung
   - Alternativweg

## Zweck dieses Ordners

Dieser Ordner soll verhindern, dass:
- Architektur implodiert,
- KI-Agenten kontextlos optimieren,
- Entscheidungen inkonsistent werden.

Er ist das Gedächtnis *über* den Repos.
