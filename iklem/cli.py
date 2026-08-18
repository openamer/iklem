"""The CLI channel — now with a real model backend.

`iklem chat` runs an interactive conversation. `iklem ask "..."` asks a
single question. Both report honest errors when the provider fails.
"""

from __future__ import annotations

import argparse
import sys

from iklem.core.agent import Agent
from iklem.memory.skills import Skill, SkillRegistry
from iklem.providers.openai_compatible import OpenAICompatibleProvider


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="iklem", description="iklem — forged, not cloned.")
    p.add_argument("--version", action="store_true", help="show version and exit")
    p.add_argument("--remember", nargs=2, metavar=("KEY", "VALUE"), help="store a memory")
    p.add_argument("--recall", metavar="KEY", help="recall a memory")
    p.add_argument("--skill", nargs=2, metavar=("NAME", "DESC"), help="add a skill")
    p.add_argument("--skills", action="store_true", help="list skills")
    p.add_argument("--gateway", action="store_true", help="start the Telegram channel")
    p.add_argument("ask", nargs="*", help="ask a question (non-interactive)")
    return p


def _make_agent() -> Agent:
    provider = OpenAICompatibleProvider()
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
        from iklem.gateway.telegram import TelegramChannel

        channel = TelegramChannel()
        channel.start(_make_agent())
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
