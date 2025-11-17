# wgx – Konzept & Blueprint v1

> **Leitfrage:** Wie bedient man ein komplexes System, ohne sich in Details zu verlieren?

**Antwort:** Ein einziges, stabiles CLI-Tool – `wgx`.

**Essenz:** `wgx` ist der **Steuer-Nerv** des Heimgewebes. Es ist das, was du im Terminal aufrufst, um den Zustand zu prüfen, Backups zu machen oder Templates auszurollen.

Kurz: wgx ist der **Bordcomputer**, der die Flotte bedient – nicht das Gehirn (hausKI) und nicht das Gedächtnis (chronik).

## Abgrenzung

-   **hausKI**: der denkende Agent, der *entscheidet*, was zu tun ist (oft asynchron).
-   **chronik**: speichert und zeigt Ereignisse (Events, Panels, Metriken).
-   **wgx**: der ausführende Befehl, der *macht*, was du (oder `hausKI`) ihm sagst.

> Wenn hausKI der Denker ist und chronik das Tagebuch,  
> dann ist `wgx` der verlässliche **Assistent**, der die Ordner anlegt, die Skripte startet und prüft, ob alles läuft.

## Kernkommandos (v1)

-   `wgx doctor`: Gesundheitscheck (Configs, Ports, Git-Status).
-   `wgx metrics snapshot`: Systemmetriken erfassen → `metrics.snapshot.json`.
-   `wgx fleet up`: Templates aus `metarepo` auf die Fleet-Repos anwenden.
-   `wgx knowledge extract`: Wissen aus Code/Docs in `knowledge.graph.jsonl` extrahieren.
-   `wgx agent run <workflow>`: Einen Agenten-Workflow ausführen.

## Prinzipien

1.  **Ein Entrypoint:** `wgx` ist der einzige Weg, mit dem System zu interagieren.
2.  **Idempotent:** Jeder `wgx`-Befehl kann mehrfach ausgeführt werden und führt zum selben Ergebnis.
3.  **Lokal-First:** `wgx` funktioniert ohne Internetverbindung.
4.  **Erklärbar:** `--dry-run` und `--verbose` zeigen, was passieren würde und was passiert ist.
5.  **Mensch & Maschine:** `wgx` ist für Menschen im Terminal und für `hausKI` in Playbooks gleichermaßen bedienbar.
