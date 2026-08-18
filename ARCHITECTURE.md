# iklem — Architecture

> **Forged, not cloned.**

## What iklem is

iklem is a self-improving personal AI agent that runs on your own machine,
meets you in the channels you already use, and gets better the longer you use
it. It is a **new project**, not a fork: it takes the best idea from each of
the three leading agent harnesses and fuses them into one coherent
architecture, then adds its own axis.

## The three ideas we fuse (and what we deliberately leave out)

| Source | Idea we take | Idea we leave out |
|---|---|---|
| **hermes-agent** | The learning loop — memory + skills that persist and improve across sessions | Its god-file `main.py` (17k lines) and the "fork without differentiation" trap |
| **deepseek-harness** | Plugin discipline — "everything is a plugin", narrow core, capability at the edges | Its TypeScript/Cordis stack and repo-specific tooling |
| **openclaw** | Platform breadth — one gateway, many channels | Its sprawling surface and community-driven bloat |

## The one axis iklem wins on

**iklem does not break, and it provably improves with use.**

- **Does not break** — every state-changing operation (update, install, sync)
  verifies before it claims and reports real errors instead of inventing
  results. Self-update is hardened against file-locks, interrupted installs,
  and stale recovery markers.
- **Provably improves** — learning is observable, not a slogan. Memory persists
  across sessions, skills are distilled from hard tasks and refined on reuse,
  and the swarm shares curated, signed, leak-free knowledge between nodes.

## Architecture principles

1. **Narrow core, capability at the edges.** The core is a small, stable
   runtime. Everything else — channels, tools, providers, skills — is a plugin.
2. **Everything is a plugin.** A plugin is a self-contained unit with a
   manifest. The core discovers, loads, and orchestrates plugins; it never
   hard-codes a specific channel or tool.
3. **Verification over fabrication.** Every operation that mutates state
   returns a verifiable result. The agent never claims success it cannot prove.
4. **Prompt-cache safety.** A long-lived conversation reuses a cached prefix.
   Nothing mutates past context or rebuilds the system prompt mid-conversation.
5. **Privacy by default.** Secrets and PII are redacted before anything is
   stored or shared.

## Module layout

```
iklem/
├── iklem/
│   ├── core/            # the narrow waist — runtime, loop, context
│   │   ├── runtime.py   #   plugin discovery + lifecycle
│   │   ├── loop.py      #   the agent loop (turn → tools → result)
│   │   └── context.py   #   system prompt, cache-safe context assembly
│   ├── memory/          # the learning loop (from hermes)
│   │   ├── store.py     #   durable memory across sessions
│   │   └── skills.py    #   skill distillation + refinement
│   ├── gateway/         # platform breadth (from openclaw)
│   │   ├── base.py      #   channel adapter ABC
│   │   └── cli.py       #   the CLI channel (first, simplest)
│   ├── plugins/         # everything is a plugin (from deepseek-harness)
│   │   └── manifest.py  #   plugin manifest + registry
│   └── verify/          # the "does not break" axis
│       └── checks.py    #   pre/post condition checks, honest error reporting
├── pyproject.toml
├── README.md
└── ARCHITECTURE.md      # this file
```

## The first milestone (what we build now)

A **working core** that proves the architecture, not a clone of anything:

1. A CLI you can actually run (`iklem`).
2. A plugin system where a channel and a tool are both plugins.
3. A memory store that persists across sessions.
4. A verify layer that reports real errors instead of fabricating results.

This is deliberately small. It is the foundation on which the full vision
(channels, swarm, brain) is built — one verified step at a time.
