"""The dehumidifier runs alongside mold-prevention heating and respects climate control off."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from .conftest import SAMPLE_ROOM, _create_coordinator, _make_store_mock, make_mock_states_get

AREA = "living_room_abc12345"
DRYER = "switch.living_room_dryer"
ROOM = {
    **SAMPLE_ROOM,
    "dehumidifier_entity": DRYER,
    "dehumidifier_enabled": True,
    "dehumidifier_lower_bound": 50,
    "dehumidifier_upper_bound": 60,
}
SETTINGS = {
    "mold_prevention_enabled": True,
    "mold_prevention_intensity": "medium",
    "outdoor_temp_sensor": "sensor.outdoor_temp",
}


async def _run_cycle(hass, mock_config_entry, dryer_state: str, settings: dict | None = None, room: dict | None = None):
    store = _make_store_mock({AREA: room or ROOM})
    store.get_settings.return_value = settings or SETTINGS
    hass.data = {"roommind": {"store": store}}
    # 18 °C, 75 % RH, 0 °C outside: critical mold risk, humidity above the upper bound
    hass.states.get = MagicMock(
        side_effect=make_mock_states_get(humidity="75.0", outdoor_temp="0.0", extra={DRYER: (dryer_state, {})})
    )
    hass.services.async_call = AsyncMock()
    coordinator = _create_coordinator(hass, mock_config_entry)
    data = await coordinator._async_update_data()
    dryer_calls = [c.args for c in hass.services.async_call.await_args_list if c.args[2].get("entity_id") == DRYER]
    return data["rooms"][AREA], dryer_calls


@pytest.mark.asyncio
async def test_dehumidifier_and_prevention_heat_act_together(hass, mock_config_entry):
    room, dryer_calls = await _run_cycle(hass, mock_config_entry, "off")
    assert room["mold_risk_level"] == "critical"
    assert room["mold_prevention_active"] is True
    assert room["target_temp"] == 23.0  # comfort 21 + medium delta 2
    assert dryer_calls == [("switch", "turn_on", {"entity_id": DRYER})]


@pytest.mark.asyncio
async def test_dehumidifier_without_prevention_leaves_target_alone(hass, mock_config_entry):
    room, dryer_calls = await _run_cycle(
        hass, mock_config_entry, "off", settings={**SETTINGS, "mold_prevention_enabled": False}
    )
    assert room["mold_prevention_active"] is False
    assert room["target_temp"] == 21.0
    assert dryer_calls == [("switch", "turn_on", {"entity_id": DRYER})]


@pytest.mark.asyncio
async def test_unreachable_dehumidifier_keeps_prevention_heat(hass, mock_config_entry):
    room, dryer_calls = await _run_cycle(hass, mock_config_entry, "unavailable")
    assert room["mold_prevention_active"] is True
    assert dryer_calls == []


@pytest.mark.asyncio
async def test_global_climate_control_off_sends_dehumidifier_nothing(hass, mock_config_entry):
    _, dryer_calls = await _run_cycle(
        hass, mock_config_entry, "off", settings={**SETTINGS, "climate_control_active": False}
    )
    assert dryer_calls == []


@pytest.mark.asyncio
async def test_room_climate_control_off_sends_dehumidifier_nothing(hass, mock_config_entry):
    _, dryer_calls = await _run_cycle(hass, mock_config_entry, "off", room={**ROOM, "climate_control_enabled": False})
    assert dryer_calls == []


@pytest.mark.asyncio
async def test_room_can_turn_prevention_heat_off_and_keep_the_dehumidifier(hass, mock_config_entry):
    room, dryer_calls = await _run_cycle(
        hass,
        mock_config_entry,
        "off",
        settings={**SETTINGS, "mold_detection_enabled": True},
        room={**ROOM, "mold_prevention_heating": False},
    )
    assert room["mold_risk_level"] == "critical"  # detection still runs for the room
    assert room["mold_prevention_active"] is False
    assert room["target_temp"] == 21.0
    assert dryer_calls == [("switch", "turn_on", {"entity_id": DRYER})]


@pytest.mark.asyncio
async def test_room_prevention_heat_alone_without_dehumidifier(hass, mock_config_entry):
    room, dryer_calls = await _run_cycle(hass, mock_config_entry, "off", room={**ROOM, "dehumidifier_enabled": False})
    assert room["mold_prevention_active"] is True
    assert room["target_temp"] == 23.0
    assert dryer_calls == []


@pytest.mark.asyncio
async def test_room_prevention_heat_needs_the_global_switch(hass, mock_config_entry):
    room, _ = await _run_cycle(
        hass,
        mock_config_entry,
        "off",
        settings={**SETTINGS, "mold_prevention_enabled": False},
        room={**ROOM, "mold_prevention_heating": True},
    )
    assert room["mold_prevention_active"] is False
    assert room["target_temp"] == 21.0
