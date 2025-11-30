# Devcontainer Varianten

Dieses Verzeichnis enthält zwei vorkonfigurierte Devcontainer:

- **devcontainer-dind.json** – Docker-in-Docker (privileged). Gut, wenn der Host kein Docker-Socket bereitstellt.
- **devcontainer-socket.json** – Docker-from-Docker via Socket-Mount. Bevorzugt, wenn ein Docker-Daemon auf dem Host läuft.

Die Versionen für `yq`, `uv` und `rust` werden anhand von `toolchain.versions.yml` synchronisiert.

## Nutzung
1. **Variante wählen:** Kopiere die gewünschte Datei nach `devcontainer.json`.
   ```bash
   cp .devcontainer/devcontainer-socket.json .devcontainer/devcontainer.json
   # oder
   cp .devcontainer/devcontainer-dind.json .devcontainer/devcontainer.json
   ```
2. **(Optional) Versionen neu synchronisieren:**
   Wenn sich `toolchain.versions.yml` ändert:
   ```bash
   bash .devcontainer/sync-from-toolchain.sh
   ```

## Hinweise
- **Security:** Der Socket-Container bindet `/var/run/docker.sock` ein. Das entspricht Root-Rechten auf dem Host – nur in vertrauenswürdigen Umgebungen verwenden. Die DinD-Variante ist isolierter, dafür ressourcenintensiver.
- **Docker-Gruppe:** Beim Socket-Container wird der User `vscode` beim Start per `usermod -aG docker` ergänzt. Falls `docker ps` direkt nach dem Start noch Rechtefehler zeigt, einmal „Reopen in Container“ ausführen.
- **Templates als Quelle:** Bearbeite die Templates (`_devcontainer-*.template.json`) und rendere die finalen Dateien anschließend mit `just devcontainer:sync`, damit `devcontainer-*.json` synchron bleiben.
