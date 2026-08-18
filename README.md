# iklem

> **Forged, not cloned.**

**iklem is the agent that does not break, and that provably improves with use.**

It runs on your own machine, meets you in the channels you already use, and
gets better the longer you use it. It is a new project — not a fork — that
fuses the best idea from each of the leading agent harnesses into one coherent
architecture, then adds its own axis.

## What it fuses

- **The learning loop** (memory + skills that persist and improve) — from the
  hermes-agent lineage.
- **Plugin discipline** ("everything is a plugin", narrow core) — from the
  deepseek-harness lineage.
- **Platform breadth** (one gateway, many channels) — from the openclaw lineage.

## What it adds

1. **It does not break.** Every state-changing operation verifies before it
   claims and reports real errors instead of inventing results.
2. **It provably improves with use.** Learning is observable, not a slogan.

## What it can do today

- **Think** — a local Ollama model (private, offline, no API key). Default
  `qwen3:1.7b` answers in ~2s; the "thinking" block is disabled by default to
  avoid CPU latency.
- **Learn** — durable memory and skills that persist across sessions.
- **Share** — a swarm of nodes exchanging signed, verifiable knowledge packets
  over an untrusted relay.
- **Reach you** — CLI, Telegram, Slack, and Discord channels, all as plugins.
- **Extend** — channels, providers, and tools are all plugins; the core stays
  narrow.

## Install

```bash
pip install -e .
```

## Run

```bash
iklem                          # interactive chat
iklem ask "what is iklem?"     # one-shot question
iklem --remember name Damir    # store a memory
iklem --recall name            # recall a memory
iklem --skill deploy "..."     # add a skill
iklem --skills                 # list skills
iklem --swarm-relay            # run a local swarm relay
iklem --swarm-publish skill "..."  # sign + publish a packet
iklem --swarm-list             # list + verify packets
```

## Configuration (environment)

| Variable | Purpose |
|---|---|
| `IKLEM_OLLAMA_MODEL` | local model (default `qwen3:1.7b`) |
| `IKLEM_OLLAMA_URL` | Ollama endpoint (default `http://localhost:11434`) |
| `IKLEM_API_KEY` / `IKLEM_BASE_URL` / `IKLEM_MODEL` | OpenAI-compatible provider |
| `IKLEM_TELEGRAM_TOKEN` | Telegram bot token |
| `IKLEM_SLACK_TOKEN` / `IKLEM_SLACK_CHANNEL` | Slack bot |
| `IKLEM_DISCORD_TOKEN` / `IKLEM_DISCORD_CHANNEL` | Discord bot |
| `IKLEM_NODE_ID` / `IKLEM_SWARM_SECRET` | swarm identity |
| `IKLEM_RELAY_URL` | swarm relay (default `http://127.0.0.1:8765`) |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design.

## License

MIT
