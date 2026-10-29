# Grabowski als kanonisches Fleet-Mitglied für RepoGround

**Stand:** 29. Oktober 2026 · **Scope:** ausschließlich bestehende Fleet- und Publikationspfade.

## Entscheidung

`heimgewebe/grabowski` wird als aktives Core-Fleet-Mitglied in `fleet/repos.yml` geführt. Der bestehende stündliche RepoGround-Fleet-Publisher liest genau diese autoritative Quelle und kann dadurch auch Grabowskis `main` revisionsgebunden aktualisieren. **Kein neuer Publisher, Timer oder Cache.**

## Nachgewiesene Ursache und Nutzwert

Am 29.10.2026 meldete RepoGround für Grabowski nur das gesunde, aber veraltete Bundle `e321ab65` vom 27.10.; der GitHub-`main`-Stand war `489a7db8`. Die aktive Fleet enthielt elf Repositories ohne Grabowski. Damit fehlte dem tatsächlich verwendeten Operator-Consumer eine automatische Aktualisierungsroute. Die Aufnahme schließt die bestehende Lücke an ihrer Quelle.

Grabowski besitzt konkrete gemeinsame Review-, Agenten- und GitHub-Verträge. Diese sind für RepoGrounds revisionsgebundene Rückwärtsbeziehungen und Folgenanalyse relevant. Der Name ist eindeutig (`heimgewebe/grabowski`, Branch `main`). Das ist mehr als eine allgemeine Organisationszugehörigkeit.

## Grenzen und Abnahme

- `fleet/repos.yml` entscheidet allein die Mitgliedschaft. Zusatzdaten, Fleet-Liste, Kompatibilitätsprojektion, Matrix und Renovate-Scope werden aus den vorhandenen Generatoren abgeleitet.
- Die Aufnahme **startet keinen** pauschalen Template-, Contract-, Workflow- oder Produktionsrollout und verleiht RepoGround keine Git-/Merge-/Deploy-Schreibbefugnis. Bestehende solche Aktionen bleiben separat autorisiert.
- Nach Integration: aktuellen GitHub-`main` von Grabowski und authentisches `grabowski`-Bundle über einen **regulären** bestehenden Fleet-Publisherlauf vergleichen. `fresh_exact` nur bei identischem Commit und sauberer Quelle behaupten. Bis dahin ist das eine integrierbare Quellkonfiguration, kein Live-Freshness-Beweis.
- Wenn Grabowski die gemeinschaftlichen Fleet-Verträge später nicht mehr braucht, Mitgliedschaft und daraus erzeugte Projektionen in einem Revert zurücknehmen. Keine historische Publikation heimlich als aktuelle deklarieren.

Quelle: [RepoGround-Optimierungsroadmap](https://github.com/heimgewebe/repoground/blob/main/docs/roadmap/repoground-vision-and-agent-adoption.md), RG-OPT-02.
