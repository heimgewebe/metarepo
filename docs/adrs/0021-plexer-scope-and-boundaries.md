# ADR-0021 Scope & Boundaries of Plexer in the Heimgewebe Organism

Status: Accepted
Datum: 2025-12-01

## Context
The Heimgewebe ecosystem introduces **Plexer** as the Event Router (Ereignisnetz)
responsible for transporting events between repositories, CI pipelines, and
high-level agents like Heimgeist.

At the same time, the system supports **PR comment commands** (Sichter, WGX,
Heimgeist), which rely on GitHub APIs, bots, and command dispatchers.

Both mechanisms use “messages”, but they serve fundamentally different
functions.

## Decision
**Plexer handles only Event Transport.
PR commands do NOT go through Plexer.**

Specifically:

### Plexer **does**:
- receive events (`POST /events`)
- validate minimal structure (`type`, `source`, `payload`)
- log and normalize events
- forward events to consumers (Heimgeist, semantAH, others)
- act as the nervous system for the Heimgewebe organism

### Plexer **must NOT**:
- receive PR comments
- parse PR commands
- communicate with GitHub APIs
- act as dispatcher, reviewer, or bot
- deal with conversational or interactive flows

### PR Commands continue to use:
- GitHub APIs
- GitHub Apps
- Command dispatch workflows
- Existing dispatcher logic in Heimgewebe repos

## Rationale

1. **Separation of Function**
   Event routing (transport) and command interpretation (control/logic)
   belong to different functional levels of the organism.

2. **Avoid Overloading Plexer**
   Mixing event streams with conversational or control flows creates ambiguity
   and turns Plexer into a pseudo-monolith.

3. **Preserve Autonomy of Tools**
   Sichter, WGX, Heimgeist commands remain directly tied to GitHub events,
   not coupled through Plexer.

4. **Scalability**
   Plexer stays replaceable, observable, and minimal.
   Heimgeist can evolve independently.

## Consequences
- All CI, deployment, and monitoring events flow through Plexer.
- All PR commands continue to flow directly from GitHub → dispatcher → tool.
- Plexer remains a lightweight, event-focused service.
- Later expansions (Kafka, Redis Streams, MQ, etc.) remain possible without
  breaking command workflows.

## Alternatives considered

1. **Route PR commands via Plexer**
   Rejected – overcoupling, wrong abstraction level.

2. **Merge Plexer into Heimgeist**
   Rejected – breaks modularity and separates concerns poorly.

3. **Create a separate PR-command-bus**
   Rejected – unnecessary complexity at this stage.

## Notes
This ADR MUST be updated before changing the message topology of Heimgewebe.
