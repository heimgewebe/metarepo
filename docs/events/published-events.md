# Published Events (`*.published.v1`)

## Konzept
Ein `published.v1` Event ist ein reines **Signal** (Pointer), kein Transport-Container.
Es informiert das Heimgewebe darüber, dass an einem kanonischen Ort (z.B. GitHub Release Assets) ein neues Artefakt verfügbar ist.

## Invarianten
1.  **Signal, kein Transport**: Das Event enthält niemals das Artefakt selbst, sondern nur einen Zeiger (`url`).
2.  **Kanonische Quelle**: Die `url` muss auf die persistente, autoritative Quelle zeigen (z.B. GitHub Releases), niemals auf den Plexer oder temporäre Caches.
3.  **Fail-Open**: Der Versand eines Notify-Events darf niemals den produzierenden Workflow abbrechen. Plexer-Ausfälle sind zu tolerieren.
4.  **Pull-Prinzip**: Konsumenten (wie Heimgeist oder HausKI) reagieren auf das Signal, indem sie die Daten bei Bedarf von der `url` abrufen. Sie ziehen keine Daten aus dem Event-Payload.

## Schema
Das Schema ist definiert in [`contracts/events/published.v1.schema.json`](../../contracts/events/published.v1.schema.json).

### Pflichtfelder Payload
- `url`: Kanonische Download-URL (HTTPS).
- `ts`: Zeitstempel des Events (Kompatibilität).
- `generated_at`: (Optional) Erstellungszeitpunkt des Artefakts.

## Validierung
Ein lokaler Guard (`.wgx/guards/published-event.sh`) kann zur Validierung genutzt werden.
**Hinweis**: Dieser Guard ist **advisory** (informativ) und fail-soft. Er führt die Validierung nur durch, wenn `ajv` in der Umgebung verfügbar ist.

## Nutzung
Produzenten senden dieses Event *nach* dem erfolgreichen Upload des Artefakts.
Der Plexer dient hierbei lediglich als Router ("Event Bus"), um Entkopplung zu gewährleisten.
