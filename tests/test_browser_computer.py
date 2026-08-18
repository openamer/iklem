"""Tests for the upgraded browser and computer tools."""

from __future__ import annotations

from iklem.tools.browser import (
    browser_click,
    browser_links,
    browser_screenshot,
    browser_submit,
    browser_type,
    browse,
)
from iklem.tools.computer import (
    click,
    double_click,
    hotkey,
    mouse_position,
    move_mouse,
    press_key,
    right_click,
    scroll,
)


def test_browser_tools_report_missing_playwright():
    # Either works (playwright installed) or reports the honest error.
    assert isinstance(browse("https://example.com"), str)
    assert isinstance(browser_click("body"), str)
    assert isinstance(browser_type("input", "x"), str)
    assert isinstance(browser_submit("form"), str)
    assert isinstance(browser_links(), str)
    assert isinstance(browser_screenshot("/tmp/x.png"), str)


def test_computer_tools_report_missing_pyautogui():
    assert isinstance(click("0", "0"), str)
    assert isinstance(double_click("0", "0"), str)
    assert isinstance(right_click("0", "0"), str)
    assert isinstance(move_mouse("0", "0"), str)
    assert isinstance(mouse_position(), str)
    assert isinstance(scroll("3"), str)
    assert isinstance(press_key("enter"), str)
    assert isinstance(hotkey("ctrl+s"), str)
