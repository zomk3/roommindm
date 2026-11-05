"""Verify dehumidifier hysteresis, risk triggers and device lifecycle."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.roommind.managers.dehumidifier_manager import DehumidifierManager


@pytest.fixture
def setup_manager():
    hass = MagicMock()
    state = MagicMock(state="off")
    hass.states.get.return_value = state
    hass.services.async_call = AsyncMock()
    room = {
        "area_id": "bathroom",
        "dehumidifier_enabled": True,
        "dehumidifier_entity": "switch.dryer",
        "dehumidifier_lower_bound": 50,
        "dehumidifier_upper_bound": 60,
    }
    return DehumidifierManager(hass), hass, state, room


@pytest.mark.asyncio
async def test_hysteresis(setup_manager):
    manager, hass, state, room = setup_manager
    with patch(
        "custom_components.roommind.managers.dehumidifier_manager.calculate_mold_risk", return_value=("ok", 55, None)
    ):
        await manager.evaluate(room, 22, 60, 15)
        hass.services.async_call.assert_awaited_once_with(
            "switch", "turn_on", {"entity_id": "switch.dryer"}, blocking=True
        )
        hass.services.async_call.reset_mock()
        state.state = "on"
        await manager.evaluate(room, 22, 55, 15)
        hass.services.async_call.assert_not_awaited()
        await manager.evaluate(room, 22, 50, 15)
        hass.services.async_call.assert_awaited_once_with(
            "switch", "turn_off", {"entity_id": "switch.dryer"}, blocking=True
        )


@pytest.mark.asyncio
async def test_risk_triggers_below_upper_bound(setup_manager):
    manager, hass, state, room = setup_manager
    with patch(
        "custom_components.roommind.managers.dehumidifier_manager.calculate_mold_risk",
        return_value=("warning", 85, None),
    ):
        await manager.evaluate(room, 18, 55, 0)
        assert hass.services.async_call.await_args.args[1] == "turn_on"
        hass.services.async_call.reset_mock()
        await manager.evaluate(room, 18, 50, 0)
        hass.services.async_call.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("humidity", [None, float("nan"), 101])
async def test_invalid_sensor_stops_device(setup_manager, humidity):
    manager, hass, state, room = setup_manager
    state.state = "on"
    await manager.evaluate(room, 22, humidity, 15)
    assert hass.services.async_call.await_args.args[1] == "turn_off"


@pytest.mark.asyncio
async def test_disable_and_reassign_stop_previous_device(setup_manager):
    manager, hass, state, room = setup_manager
    await manager.evaluate(room, 22, 65, 15)
    state.state = "on"
    room["dehumidifier_entity"] = "humidifier.dryer"
    await manager.evaluate(room, 22, 65, 15)
    assert hass.services.async_call.await_args.args == ("switch", "turn_off", {"entity_id": "switch.dryer"})
    room["dehumidifier_enabled"] = False
    await manager.evaluate(room, 22, 65, 15)
    assert hass.services.async_call.await_args.args == ("humidifier", "turn_off", {"entity_id": "humidifier.dryer"})
    assert not manager._entities


@pytest.mark.asyncio
async def test_removed_room_stops_device(setup_manager):
    manager, hass, state, room = setup_manager
    await manager.evaluate(room, 22, 65, 15)
    state.state = "on"
    await manager.remove_room("bathroom")
    assert hass.services.async_call.await_args.args[1] == "turn_off"
    assert not manager._entities
