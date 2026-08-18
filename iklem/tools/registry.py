"""Tool registry — the full set of tools the agent can call.

A tool is a named callable with a description. The agent loop exposes these
to the model so it can call them to learn facts and act instead of guessing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from iklem.tools import browser, code, computer, cron, delegate, files, git, http, memory, process, selfextend, selfmodify, session, shell, skills, system, tts, util, vision, web


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
        Tool(name="git_status", description="Return the git status of the iklem repo.", fn=git.git_status),
        Tool(name="git_diff", description="Return the uncommitted diff of the iklem repo.", fn=git.git_diff),
        Tool(name="git_commit", description="Commit all changes with a message.", fn=git.git_commit),
        Tool(name="git_push", description="Push committed changes to the remote.", fn=git.git_push),
        Tool(name="cron_schedule", description="Schedule a command to run every N seconds.", fn=cron.cron_schedule),
        Tool(name="cron_list", description="List all scheduled jobs.", fn=cron.cron_list),
        Tool(name="cron_remove", description="Remove a scheduled job.", fn=cron.cron_remove),
        Tool(name="delegate_task", description="Run a task in a fresh subagent and return its result.", fn=delegate.delegate_task),
        Tool(name="delegate_with_role", description="Run a task in a subagent with a role (researcher/coder/writer/reviewer).", fn=delegate.delegate_with_role),
        Tool(name="delegate_batch", description="Run multiple tasks (one per line) in parallel subagents.", fn=delegate.delegate_batch),
        Tool(name="delegate_pipeline", description="Run tasks sequentially, feeding each result into the next (roles comma-separated).", fn=delegate.delegate_pipeline),
        Tool(name="browse", description="Open a URL in a real browser and return the rendered text.", fn=browser.browse),
        Tool(name="screenshot", description="Take a screenshot and return its file path.", fn=computer.screenshot),
        Tool(name="click", description="Click at screen coordinates (x, y).", fn=computer.click),
        Tool(name="type_text", description="Type text at the current cursor position.", fn=computer.type_text),
        Tool(name="write_file", description="Write text content to a file.", fn=files.write_file),
        Tool(name="search_files", description="Search file contents for a substring under a directory.", fn=files.search_files),
        Tool(name="copy_file", description="Copy a file from src to dst.", fn=files.copy_file),
        Tool(name="move_file", description="Move (rename) a file from src to dst.", fn=files.move_file),
        Tool(name="delete_file", description="Delete a file or empty directory.", fn=files.delete_file),
        Tool(name="http_request", description="Make an HTTP request (GET/POST/PUT/DELETE) and return the response.", fn=http.http_request),
        Tool(name="weather", description="Return current weather for a city (open-meteo, no key).", fn=http.weather),
        Tool(name="json_parse", description="Parse a JSON string and return it pretty-printed.", fn=util.json_parse),
        Tool(name="math_eval", description="Evaluate a safe arithmetic expression.", fn=util.math_eval),
        Tool(name="world_time", description="Return the current time in an IANA timezone.", fn=util.world_time),
        Tool(name="random_uuid", description="Return a random UUID v4.", fn=util.random_uuid),
        Tool(name="random_number", description="Return a random integer between low and high.", fn=util.random_number),
        Tool(name="list_processes", description="List running processes (name + PID).", fn=process.list_processes),
        Tool(name="kill_process", description="Terminate a process by its PID.", fn=process.kill_process),
        Tool(name="search_sessions", description="Search past conversations and memories for a keyword.", fn=session.search_sessions),
        Tool(name="describe_image", description="Describe the contents of an image file using a vision model.", fn=vision.describe_image),
        Tool(name="speak", description="Convert text to speech and play it.", fn=tts.speak),
        Tool(name="speak_to_file", description="Convert text to speech and save it to an audio file.", fn=tts.speak_to_file),
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
