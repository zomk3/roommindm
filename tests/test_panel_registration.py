"""Sidebar panel registration."""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.roommind import _async_register_panel
from custom_components.roommind.const import DOMAIN, VERSION

pytestmark = pytest.mark.asyncio


async def test_the_panel_is_for_admins_only(hass):
    """The panel edits the whole setup; non-admins keep the dashboard card and the room entities."""
    hass.data[DOMAIN] = {}
    hass.http.async_register_static_paths = AsyncMock()
    with (
        patch.object(Path, "exists", return_value=True),
        patch("custom_components.roommind.async_register_built_in_panel") as register,
    ):
        await _async_register_panel(hass)

    register.assert_called_once()
    assert register.call_args.kwargs["require_admin"] is True
    assert register.call_args.kwargs["frontend_url_path"] == "roommind"


async def _panel_url(hass, read_bytes):
    hass.data[DOMAIN] = {}
    hass.http.async_register_static_paths = AsyncMock()
    with (
        patch.object(Path, "exists", return_value=True),
        patch.object(Path, "read_bytes", read_bytes),
        patch("custom_components.roommind.async_register_built_in_panel") as register,
    ):
        await _async_register_panel(hass)
    (config,) = hass.http.async_register_static_paths.await_args.args[0]
    return config.url_path, register.call_args.kwargs["config"]["_panel_custom"]["js_url"]


async def test_the_panel_url_carries_the_bundle_hash(hass):
    """A cached panel of the previous build must not be reused after an update, also when
    a local deploy keeps the version."""
    path, js_url = await _panel_url(hass, lambda _self: b"panel build")
    assert js_url == f"{path}?v={hashlib.sha256(b'panel build').hexdigest()[:12]}"


async def test_the_panel_url_carries_the_version_when_the_bundle_cannot_be_read(hass):
    def unreadable(_self):
        raise OSError("gone")

    path, js_url = await _panel_url(hass, unreadable)
    assert js_url == f"{path}?v={VERSION}"
