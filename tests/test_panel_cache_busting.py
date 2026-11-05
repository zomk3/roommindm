"""The panel URL carries a content hash, so a new build is never served from a stale cache."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.roommind import _async_register_panel, _file_hash
from custom_components.roommind.const import DOMAIN


def test_file_hash_changes_with_content(tmp_path):
    f = tmp_path / "panel.js"
    f.write_text("old")
    old = _file_hash(f)
    f.write_text("new")
    assert _file_hash(f) != old
    assert len(old) == 12


@pytest.mark.asyncio
async def test_panel_js_url_has_content_hash():
    hass = MagicMock()
    hass.data = {DOMAIN: {}}
    hass.http.async_register_static_paths = AsyncMock()
    hass.async_add_executor_job = AsyncMock(side_effect=lambda fn, *args: fn(*args))
    with (
        patch("custom_components.roommind.async_register_built_in_panel") as register,
        patch("custom_components.roommind._file_hash", return_value="abc123def456"),
        patch.object(Path, "exists", return_value=True),  # the built bundle is not in the repo
    ):
        await _async_register_panel(hass)
    js_url = register.call_args.kwargs["config"]["_panel_custom"]["js_url"]
    assert js_url == "/roommind/roommind-panel.js?v=abc123def456"
    static = hass.http.async_register_static_paths.await_args.args[0][0]
    assert static.url_path == "/roommind/roommind-panel.js"
