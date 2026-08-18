"""The CLI channel — now with a real model backend.

`iklem chat` runs an interactive conversation. `iklem ask "..."` asks a
single question. Both report honest errors when the provider fails.
"""

from __future__ import annotations

import argparse
import os
import sys

from iklem.core.agent import Agent
from iklem.memory.skills import Skill, SkillRegistry


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="iklem", description="iklem — forged, not cloned.")
    p.add_argument("--version", action="store_true", help="show version and exit")
    p.add_argument("--remember", nargs=2, metavar=("KEY", "VALUE"), help="store a memory")
    p.add_argument("--recall", metavar="KEY", help="recall a memory")
    p.add_argument("--skill", nargs=2, metavar=("NAME", "DESC"), help="add a skill")
    p.add_argument("--skills", action="store_true", help="list skills")
    p.add_argument("--gateway", action="store_true", help="start the Telegram channel")
    p.add_argument("--swarm-sign", nargs=3, metavar=("NODE", "KIND", "CONTENT"), help="sign a knowledge packet")
    p.add_argument("--swarm-relay", action="store_true", help="run a local swarm relay")
    p.add_argument("--swarm-publish", nargs=2, metavar=("KIND", "CONTENT"), help="sign and publish a packet to the relay")
    p.add_argument("--swarm-list", action="store_true", help="list packets from the relay")
    p.add_argument("--server", action="store_true", help="run the HTTP server (desktop app backend)")
    p.add_argument("ask", nargs="*", help="ask a question (non-interactive)")
    return p


def _make_agent() -> Agent:
    # Prefer a local Ollama model (private, no key) when reachable; fall back
    # to the OpenAI-compatible provider otherwise.
    from iklem.providers.ollama import OllamaProvider

    provider = OllamaProvider()
    return Agent(provider=provider)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.version:
        print("iklem 0.1.0")
        return 0

    from iklem.core.runtime import Runtime

    runtime = Runtime()
    skills = SkillRegistry(runtime.memory)

    if args.remember:
        key, value = args.remember
        runtime.memory.set(key, value)
        print(f"✓ remembered {key}")
        return 0

    if args.recall:
        value = runtime.memory.get(args.recall)
        print(value if value is not None else "(no memory)")
        return 0

    if args.skill:
        name, desc = args.skill
        skills.add(Skill(name=name, description=desc))
        print(f"✓ skill '{name}' added")
        return 0

    if args.skills:
        names = skills.names()
        if not names:
            print("(no skills yet)")
        else:
            for n in names:
                print(f"  • {n}")
        return 0

    if args.gateway:
        from iklem.gateway.gateway import run_gateway

        return run_gateway(_make_agent())

    if args.swarm_sign:
        from iklem.swarm.packet import KnowledgePacket, is_leak_free

        node, kind, content = args.swarm_sign
        if not is_leak_free(content):
            print("✗ content looks like it contains a secret — refusing to sign")
            return 1
        pkt = KnowledgePacket(node_id=node, kind=kind, content=content)
        pkt.sign(os.environ.get("IKLEM_SWARM_SECRET", "dev-secret"))
        print(f"✓ signed packet (node={node}, kind={kind})")
        print(f"  signature: {pkt.signature[:16]}…")
        return 0

    if args.swarm_relay:
        from iklem.swarm.relay import serve

        serve()
        return 0

    if args.swarm_publish:
        from iklem.swarm.node import Node, RelayClient
        from iklem.swarm.packet import is_leak_free

        kind, content = args.swarm_publish
        if not is_leak_free(content):
            print("✗ content looks like it contains a secret — refusing to publish")
            return 1
        node = Node.from_env()
        pkt = node.sign(kind, content)
        relay = RelayClient(os.environ.get("IKLEM_RELAY_URL", "http://127.0.0.1:8765"))
        if relay.publish(pkt):
            print(f"✓ published (node={node.node_id}, kind={kind})")
            return 0
        print("✗ publish failed — is the relay running? (iklem --swarm-relay)")
        return 1

    if args.swarm_list:
        from iklem.swarm.node import Node, RelayClient

        node = Node.from_env()
        relay = RelayClient(os.environ.get("IKLEM_RELAY_URL", "http://127.0.0.1:8765"))
        packets = relay.list()
        if not packets:
            print("(no packets on relay)")
            return 0
        for pkt in packets:
            verified = "✓" if node.verify(pkt) else "✗ tampered"
            print(f"  [{verified}] {pkt.node_id}/{pkt.kind}: {pkt.content[:60]}")
        return 0

    if args.server:
        from iklem.server import serve

        serve()
        return 0

    if args.ask:
        agent = _make_agent()
        result = agent.respond(" ".join(args.ask))
        if result.ok:
            print(result.content)
            return 0
        print(f"✗ {result.error}", file=sys.stderr)
        return 1

    # Default: interactive chat
    agent = _make_agent()
    print("iklem — forged, not cloned. (type 'exit' to quit)")
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip().lower() in {"exit", "quit"}:
            break
        if not line.strip():
            continue
        result = agent.respond(line)
        if result.ok:
            print(result.content)
        else:
            print(f"✗ {result.error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
