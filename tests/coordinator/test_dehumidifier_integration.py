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
    "dehumidifier_delay_minutes": 0,  # these tests check what switches, not when
}


async def _run_cycle(
    hass,
    mock_config_entry,
    dryer_state: str,
    settings: dict | None = None,
    room: dict | None = None,
    extra: dict | None = None,
    window_sensors: dict | None = None,
):
    store = _make_store_mock({AREA: room or ROOM})
    store.get_settings.return_value = settings or SETTINGS
    hass.data = {"roommind": {"store": store}}
    # 18 °C, 75 % RH, 0 °C outside: critical mold risk, humidity above the upper bound
    hass.states.get = MagicMock(
        side_effect=make_mock_states_get(
            humidity="75.0",
            outdoor_temp="0.0",
            extra={DRYER: (dryer_state, {}), **(extra or {})},
            window_sensors=window_sensors,
        )
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


@pytest.mark.asyncio
async def test_room_state_reports_running_dehumidifier(hass, mock_config_entry):
    room, _ = await _run_cycle(hass, mock_config_entry, "on")
    assert room["dehumidifier_active"] is True
    assert room["dehumidifier_lower_bound"] == 50


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("dryer_state", "room_extra"),
    [("off", {}), ("on", {"dehumidifier_enabled": False}), ("on", {"climate_control_enabled": False})],
)
async def test_room_state_reports_no_dehumidifier_when_not_running_for_roommind(
    hass, mock_config_entry, dryer_state, room_extra
):
    room, _ = await _run_cycle(hass, mock_config_entry, dryer_state, room={**ROOM, **room_extra})
    assert room["dehumidifier_active"] is False


@pytest.mark.asyncio
async def test_default_delay_holds_back_the_first_switch(hass, mock_config_entry):
    settings = {k: v for k, v in SETTINGS.items() if k != "dehumidifier_delay_minutes"}
    room, dryer_calls = await _run_cycle(hass, mock_config_entry, "off", settings=settings)
    assert dryer_calls == []  # condition must hold 10 minutes first
    assert room["mold_prevention_active"] is True  # prevention heat is not delayed by this


@pytest.mark.asyncio
async def test_full_tank_brings_prevention_heat_back_although_the_room_turned_it_off(hass, mock_config_entry):
    room = {**ROOM, "mold_prevention_heating": False, "dehumidifier_tank_sensor": "binary_sensor.dryer_tank"}
    with_tank, calls = await _run_cycle(
        hass, mock_config_entry, "off", room=room, extra={"binary_sensor.dryer_tank": ("on", {})}
    )
    assert with_tank["mold_prevention_active"] is True  # fallback while the dehumidifier cannot work
    assert with_tank["dehumidifier_status"] == "tank_full"
    assert calls == []
    emptied, calls = await _run_cycle(
        hass, mock_config_entry, "off", room=room, extra={"binary_sensor.dryer_tank": ("off", {})}
    )
    assert emptied["mold_prevention_active"] is False
    assert calls == [("switch", "turn_on", {"entity_id": DRYER})]


@pytest.mark.asyncio
async def test_open_window_keeps_the_dehumidifier_off(hass, mock_config_entry):
    room = {**ROOM, "window_sensors": ["binary_sensor.living_window"]}
    state, calls = await _run_cycle(
        hass, mock_config_entry, "on", room=room, window_sensors={"binary_sensor.living_window": "on"}
    )
    assert calls == [("switch", "turn_off", {"entity_id": DRYER})]
