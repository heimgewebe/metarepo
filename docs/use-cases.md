# Anwendungsfälle (User-Stories)

## 1. Tägliches Wissens-Digest

-   **User:** Ich möchte jeden Morgen eine Zusammenfassung dessen, was gestern in meinem digitalen Garten (Vault) passiert ist.
-   **Flow:**
    1.  **semantAH** analysiert `vault-gewebe` (Git-Historie, Dateiänderungen).
    2.  `semantAH` erzeugt `insights/today.json` mit den wichtigsten Änderungen.
    3.  **leitstand** (UI) zeigt dieses Digest im Panel „Heute“ an.
-   **Komponenten:** `semantAH`, `leitstand`.

## 2. Proaktiver Backup-Hinweis

-   **User:** Das System soll mich warnen, wenn ein Backup sinnvoll wäre, aber nicht automatisch laufen.
-   **Flow:**
    1.  **wgx** erzeugt stündlich `metrics.snapshot.json` (CPU-Last, Netz-Traffic, offene Dateien).
    2.  **hausKI** liest den Snapshot.
    3.  **heimlern**-Policy `suggest_backup` prüft: „last_backup > 24h && cpu_load < 0.2 && network_traffic < 1Mbit“.
    4.  Wenn ja, sendet `hausKI` ein `user.notification`-Event.
    5.  **leitstand** (UI) zeigt an: „Guter Zeitpunkt für ein Backup. Jetzt starten?“
-   **Komponenten:** `wgx`, `hausKI`, `heimlern`, `leitstand`.

## 3. Automatisierte Test-Ausführung

-   **User:** Wenn ich an einem `Justfile` arbeite, soll automatisch der `lint`-Befehl ausgeführt werden.
-   **Flow:**
    1.  **mitschreiber** erkennt, dass `Justfile` im Fokus ist (`os.context.intent`).
    2.  Event geht an **chronik**.
    3.  **hausKI** hat ein Playbook: `trigger: on_context(file == "Justfile") → run: wgx just lint`.
    4.  `hausKI` führt den Job aus.
    5.  **chronik** speichert das Job-Ergebnis (Erfolg/Fehler).
    6.  **leitstand** zeigt im Panel „PC“ den letzten `lint`-Lauf an.
-   **Komponenten:** `mitschreiber`, `chronik`, `hausKI`, `leitstand`.

## 4. Debugging & Audit

-   **User:** Ich will nachvollziehen, warum gestern Abend der Server neu gestartet wurde.
-   **Flow:**
    1.  User öffnet **leitstand** (UI).
    2.  Filtert im „Audit“-Panel nach `event_type: system.reboot`.
    3.  Findet das Event, inklusive `policy.decision`, das den Reboot ausgelöst hat.
    4.  Kann von dort zur `heimlern`-Policy und dem `metrics.snapshot` springen, der zur Entscheidung führte.
-   **Komponenten:** `chronik`, `leitstand`.
