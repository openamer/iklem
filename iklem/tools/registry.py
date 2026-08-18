"""Tool registry — the full set of tools the agent can call.

A tool is a named callable with a description. The agent loop exposes these
to the model so it can call them to learn facts and act instead of guessing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from iklem.tools import memory, shell, system, web


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    fn: Callable[..., Any]

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.fn(*args, **kwargs)


def all_tools() -> list[Tool]:
    """The complete tool set available to the agent."""
    return [
        Tool(name="current_time", description="Current local time (HH:MM:SS).", fn=system.current_time),
        Tool(name="current_date", description="Today's date (ISO, e.g. 2026-08-18).", fn=system.current_date),
        Tool(name="current_datetime", description="Full current date and time.", fn=system.current_datetime),
        Tool(name="system_info", description="OS, machine, and Python version.", fn=system.system_info),
        Tool(name="read_file", description="Read a text file's contents.", fn=system.read_file),
        Tool(name="list_dir", description="List entries in a directory.", fn=system.list_dir),
        Tool(name="fetch_url", description="Fetch a URL and return its text.", fn=web.fetch_url),
        Tool(name="search_web", description="Search Wikipedia and return result summaries.", fn=web.search_wikipedia),
        Tool(name="run_command", description="Run a shell command and return its output.", fn=shell.run_command),
        Tool(name="open_app", description="Open/launch an application by name (e.g. 'brave', 'notepad').", fn=shell.open_app),
        Tool(name="remember", description="Persist a fact under a key so it survives across sessions.", fn=memory.remember),
        Tool(name="recall", description="Retrieve a previously remembered fact by key.", fn=memory.recall),
        Tool(name="list_memories", description="List all remembered keys.", fn=memory.list_memories),
        Tool(name="echo", description="Return the input unchanged.", fn=lambda text: text),
        Tool(name="word_count", description="Count words in a string.", fn=lambda text: str(len(text.split()))),
    ]


def tool_by_name(name: str) -> Tool | None:
    for t in all_tools():
        if t.name == name:
            return t
    return None
