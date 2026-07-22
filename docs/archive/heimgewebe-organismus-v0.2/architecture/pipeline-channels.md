# Heimgewebe Message Channels

Heimgewebe uses two conceptually separate message channels:

1. **Event Channel – via Plexer**
2. **Command Channel – via GitHub PR comments**

They must remain separate by design.

## 1. Event Channel (Plexer)

The Event Channel is the nervous system of the organism.
It transports facts about what happened:

- CI results (`ci.result`)
- deployments (`deploy.started`, `deploy.succeeded`, `deploy.failed`)
- incidents (`incident.detected`)
- semantic or monitoring signals

Events are:

- pushed to **Plexer** (`POST /events`)
- validated for minimal structure (`type`, `source`, `payload`)
- logged and normalized
- forwarded to consumers (Heimgeist, semantAH, etc.)

This channel is **append-only**, factual and non-interactive.

## 2. Command Channel (PR comments)

The Command Channel is the conversational layer between humans and tools.
It transports intentions and requests:

- `@heimgewebe/sichter /quick`
- `@heimgewebe/wgx /guard changed`
- `@heimgewebe/heimlern /pattern-bad sql-injection`
- `@heimgewebe/metarepo /link-epic EPIC-123`

Commands are:

- created as PR comments on GitHub
- parsed by a dispatcher
- routed directly to the respective tool (Sichter, WGX, Heimgeist, Heimlern)

This channel is **interactive** and tightly bound to GitHub semantics.

## 3. Why the separation matters

- **Different semantics**
  - Events describe *what happened*.
  - Commands express *what should happen next*.

- **Different lifecycles**
  - Events are archived, correlated, analyzed.
  - Commands are short-lived and resolve into actions or no-ops.

- **Different failure modes**
  - Event backlog is acceptable as long as it is drained eventually.
  - Command delays directly affect developer feedback loops.

## 4. Role of Plexer

Plexer sits exclusively on the **Event Channel**:

- It never receives PR comments.
- It never parses GitHub command syntax.
- It never talks to GitHub APIs.

Plexer remains a focused Event Router and can be replaced or scaled
without touching the command workflows.

## 5. Implications

- New Heimgewebe repos should:
  - send CI / deploy / incident events to Plexer,
  - but keep PR commands as direct GitHub comment workflows.

- Any proposal to route commands through Plexer must update ADR-0021.
