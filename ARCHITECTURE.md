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

- **Does not break** — every state-changing operation verifies before it
  claims and reports real errors instead of inventing results. A tool that
  fails returns an honest error; the agent never fabricates a fact it can
  look up.
- **Provably improves** — learning is observable, not a slogan. Memory and
  conversation history persist across sessions, skills are distilled from
  hard tasks and refined on reuse, and the swarm shares curated, signed,
  leak-free knowledge between nodes.

## Architecture principles

1. **Narrow core, capability at the edges.** The core is a small, stable
   runtime. Everything else — channels, tools, providers, skills — is a plugin.
2. **Everything is a plugin.** A plugin is a self-contained unit with a
   manifest. The core discovers, loads, and orchestrates plugins; it never
   hard-codes a specific channel or tool.
3. **Verification over fabrication.** Every operation that mutates state
   returns a verifiable result. The agent never claims success it cannot prove.
4. **Grounding over guessing.** The agent calls tools to learn facts (date,
   time, system info, web, shell) instead of hallucinating them.
5. **Privacy by default.** Secrets and PII are redacted before anything is
   stored or shared.

## Module layout

```
iklem/
├── iklem/
│   ├── core/            # the narrow waist
│   │   ├── runtime.py   #   wires memory + plugins together
│   │   └── agent.py     #   the agent loop (turn → tools → grounded answer)
│   ├── memory/          # the learning loop (from hermes)
│   │   ├── store.py     #   durable memory across sessions
│   │   ├── history.py   #   persistent conversation history
│   │   └── skills.py    #   skill distillation + refinement
│   ├── providers/       # model backends (plugins)
│   │   ├── base.py      #   Provider ABC + Message/Result types
│   │   ├── ollama.py    #   local Ollama (native tool calling)
│   │   └── openai_compatible.py  # OpenAI/OpenRouter
│   ├── tools/           # the agent's capabilities (plugins)
│   │   ├── registry.py  #   the full tool set
│   │   ├── system.py    #   date/time/system/file tools
│   │   ├── web.py       #   fetch_url + Wikipedia search + summary
│   │   ├── shell.py     #   run_command + open_app
│   │   ├── code.py      #   run_python (execute Python snippets)
│   │   ├── memory.py    #   remember/recall/list_memories
│   │   └── skills.py    #   save_skill/list_skills/get_skill
│   ├── gateway/         # platform breadth (from openclaw)
│   │   ├── base.py      #   channel adapter ABC
│   │   ├── gateway.py   #   one process fans out to all channels
│   │   ├── telegram.py  #   Telegram channel
│   │   ├── slack.py     #   Slack channel
│   │   ├── discord.py   #   Discord channel
│   │   ├── whatsapp.py  #   WhatsApp Cloud API channel
│   │   └── signal.py    #   Signal channel (via signal-cli)
│   ├── swarm/           # nodes share signed knowledge
│   │   ├── packet.py    #   signed, leak-free knowledge packets
│   │   ├── node.py      #   node identity + sign/verify
│   │   └── relay.py     #   untrusted HTTP store-and-forward relay (persistent)
│   ├── plugins/         # everything is a plugin (from deepseek-harness)
│   │   ├── manifest.py  #   plugin manifest + registry
│   │   └── discovery.py #   runtime plugin loading from a directory
│   ├── server.py        #   HTTP JSON API + session persistence
│   ├── webui.py         #   self-contained browser UI served at /
│   ├── doctor.py        #   health-check command (the "does not break" axis)
│   └── verify/          # the "does not break" axis
│       └── checks.py    #   pre/post condition checks, honest error reporting
├── desktop/             # Electron desktop app (chat, sessions, settings)
├── tests/               # 58 tests, all green
├── .github/workflows/   # CI (runs tests on push/PR)
├── pyproject.toml
├── README.md
├── LICENSE
└── ARCHITECTURE.md      # this file
```

## What works today

- **Think** — a local Ollama model (private, offline) or any OpenAI-compatible
  endpoint. Default is a cloud model for reliable tool-calling.
- **Act** — the agent calls tools (date, time, system, web, shell, open_app)
  and answers from real data, not guesses.
- **Learn** — memory and conversation history persist across sessions; a fresh
  session recalls what it was told before.
- **Share** — the swarm exchanges signed, verifiable knowledge packets over an
  untrusted relay.
- **Reach you** — CLI, Telegram, Slack, and Discord channels, all as plugins.
- **Extend** — channels, tools, and providers are plugins; new plugins are
  discovered at runtime from a directory.

## What is next

1. **More tools** — richer capabilities (structured web search, code execution
   sandbox, calendar/email).
2. **A real gateway** — a single process that fans out to all channels.
3. **Skill distillation** — automatically turn hard tasks into reusable skills.
4. **Swarm transport** — a public relay so nodes can share beyond localhost.
