"""Tool registry — the full set of tools the agent can call.

A tool is a named callable with a description. The agent loop exposes these
to the model so it can call them to learn facts and act instead of guessing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from iklem.tools import code, memory, selfextend, selfmodify, shell, skills, system, web


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    fn: Callable[..., Any]

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.fn(*args, **kwargs)


def _builtin_tools() -> list[Tool]:
    """The built-in tool set."""
    return [
        Tool(name="current_time", description="Current local time (HH:MM:SS).", fn=system.current_time),
        Tool(name="current_date", description="Today's date (ISO, e.g. 2026-08-18).", fn=system.current_date),
        Tool(name="current_datetime", description="Full current date and time.", fn=system.current_datetime),
        Tool(name="system_info", description="OS, machine, and Python version.", fn=system.system_info),
        Tool(name="read_file", description="Read a text file's contents.", fn=system.read_file),
        Tool(name="list_dir", description="List entries in a directory.", fn=system.list_dir),
        Tool(name="fetch_url", description="Fetch a URL and return its text.", fn=web.fetch_url),
        Tool(name="search_web", description="Search Wikipedia and return result summaries.", fn=web.search_wikipedia),
        Tool(name="wikipedia_summary", description="Return the full intro of a Wikipedia article by title.", fn=web.wikipedia_summary),
        Tool(name="run_command", description="Run a shell command and return its output.", fn=shell.run_command),
        Tool(name="run_python", description="Execute a Python snippet and return its output.", fn=code.run_python),
        Tool(name="open_app", description="Open/launch an application by name (e.g. 'brave', 'notepad').", fn=shell.open_app),
        Tool(name="remember", description="Persist a fact under a key so it survives across sessions.", fn=memory.remember),
        Tool(name="recall", description="Retrieve a previously remembered fact by key.", fn=memory.recall),
        Tool(name="list_memories", description="List all remembered keys.", fn=memory.list_memories),
        Tool(name="save_skill", description="Save a reusable procedure (name, description, newline-separated steps).", fn=skills.save_skill),
        Tool(name="list_skills", description="List all saved skills with descriptions.", fn=skills.list_skills),
        Tool(name="get_skill", description="Retrieve a saved skill's steps by name.", fn=skills.get_skill),
        Tool(name="echo", description="Return the input unchanged.", fn=lambda text: text),
        Tool(name="word_count", description="Count words in a string.", fn=lambda text: str(len(text.split()))),
        Tool(name="self_extend", description="Create a new tool from Python code (sandboxed + verified).", fn=selfextend.self_extend),
        Tool(name="list_my_tools", description="List the tools I created myself.", fn=selfextend.list_my_tools),
        Tool(name="read_my_tool", description="Return the source code of one of my self-created tools.", fn=selfextend.read_my_tool),
        Tool(name="fix_my_tool", description="Rewrite one of my self-created tools to fix a bug (verified + rollback).", fn=selfextend.fix_my_tool),
        Tool(name="self_modify", description="Modify a core file, gated by the test suite (rollback on failure).", fn=selfmodify.self_modify_tool),
    ]


def _extension_tools() -> list[Tool]:
    """Load self-created tools from the sandbox (verified, rolled back on failure)."""
    from iklem.selfextend import load_extensions

    tools = []
    for name, description, fn in load_extensions():
        tools.append(Tool(name=name, description=description, fn=fn))
    return tools


def all_tools() -> list[Tool]:
    """The complete tool set: built-ins plus self-created extensions."""
    return _builtin_tools() + _extension_tools()


def tool_by_name(name: str) -> Tool | None:
    for t in all_tools():
        if t.name == name:
            return t
    return None
