"""Config entry unload: the sidebar panel and dashboard card go away and come back on the next setup."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.roommind import (
    CARD_URL,
    _async_register_card,
    _async_register_panel,
    async_unload_entry,
)
from custom_components.roommind.const import DOMAIN, VERSION

pytestmark = pytest.mark.asyncio


@pytest.fixture
def loaded_hass(hass, store):
    """RoomMind as after a setup: store loaded, static paths served."""
    hass.data[DOMAIN] = {"store": store}
    hass.http.async_register_static_paths = AsyncMock()
    return hass


async def _register_frontend(hass) -> MagicMock:  # noqa: ANN001
    with (
        patch.object(Path, "exists", return_value=True),
        patch("custom_components.roommind.async_register_built_in_panel") as register_panel,
        patch("custom_components.roommind.add_extra_js_url"),
    ):
        await _async_register_panel(hass)
        await _async_register_card(hass)
    return register_panel


async def _unload(hass, entry, *, ok: bool = True) -> tuple[bool, MagicMock, MagicMock]:  # noqa: ANN001
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=ok)
    with (
        patch("custom_components.roommind.async_release_all_valves", AsyncMock()),
        patch("custom_components.roommind.async_remove_panel") as remove_panel,
        patch("custom_components.roommind.remove_extra_js_url") as remove_card,
    ):
        result = await async_unload_entry(hass, entry)
    return result, remove_panel, remove_card


async def test_unloading_removes_panel_and_card(loaded_hass, mock_config_entry):
    """The store stays in hass.data, which once kept the panel in the sidebar forever."""
    await _register_frontend(loaded_hass)

    ok, remove_panel, remove_card = await _unload(loaded_hass, mock_config_entry)

    assert ok is True
    remove_panel.assert_called_once_with(loaded_hass, "roommind")
    remove_card.assert_called_once_with(loaded_hass, f"{CARD_URL}?v={VERSION}")
    assert "store" in loaded_hass.data[DOMAIN]


async def test_the_next_setup_registers_the_panel_again(loaded_hass, mock_config_entry):
    await _register_frontend(loaded_hass)
    await _unload(loaded_hass, mock_config_entry)

    register_panel = await _register_frontend(loaded_hass)

    register_panel.assert_called_once()


async def test_a_failed_unload_keeps_panel_and_card(loaded_hass, mock_config_entry):
    await _register_frontend(loaded_hass)

    ok, remove_panel, remove_card = await _unload(loaded_hass, mock_config_entry, ok=False)

    assert ok is False
    remove_panel.assert_not_called()
    remove_card.assert_not_called()


async def test_unloading_without_a_registered_panel_removes_nothing(loaded_hass, mock_config_entry):
    """Missing bundles (dev checkout): nothing was registered, so nothing is removed."""
    _, remove_panel, remove_card = await _unload(loaded_hass, mock_config_entry)

    remove_panel.assert_not_called()
    remove_card.assert_not_called()
