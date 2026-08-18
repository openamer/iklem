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

## Install

```bash
pip install -e .
```

## Run

```bash
iklem              # start the CLI
iklem --version    # show version
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design.

## License

MIT
