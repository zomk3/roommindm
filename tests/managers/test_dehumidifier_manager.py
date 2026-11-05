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


def _multi_state_manager(states: dict[str, str]):
    """A manager whose hass reports a separate state per entity (missing entity = None)."""
    hass = MagicMock()
    hass.states.get.side_effect = lambda eid: MagicMock(state=states[eid]) if eid in states else None
    hass.services.async_call = AsyncMock()
    return DehumidifierManager(hass), hass


def _room(entity: str, area_id: str = "bathroom", **extra) -> dict:
    return {
        "area_id": area_id,
        "dehumidifier_enabled": True,
        "dehumidifier_entity": entity,
        "dehumidifier_lower_bound": 50,
        "dehumidifier_upper_bound": 60,
        **extra,
    }


def _calls(hass) -> list[tuple]:
    return [c.args for c in hass.services.async_call.await_args_list]


@pytest.mark.asyncio
async def test_unreachable_old_device_does_not_block_replacement():
    states = {"switch.old": "on", "switch.new": "off"}
    manager, hass = _multi_state_manager(states)
    await manager.evaluate(_room("switch.old"), 22, 70, 15)
    states["switch.old"] = "unavailable"
    await manager.evaluate(_room("switch.new"), 22, 70, 15)
    assert ("switch", "turn_on", {"entity_id": "switch.new"}) in _calls(hass)
    assert manager._entities == {"bathroom": "switch.new"}


@pytest.mark.asyncio
async def test_released_unreachable_device_is_switched_off_when_back():
    states = {"switch.old": "on", "switch.new": "on"}
    manager, hass = _multi_state_manager(states)
    await manager.evaluate(_room("switch.old"), 22, 55, 15)
    states["switch.old"] = "unavailable"
    await manager.evaluate(_room("switch.new"), 22, 55, 15)
    assert not _calls(hass)
    states["switch.old"] = "on"
    await manager.async_retry_pending_off({"bathroom": _room("switch.new")})
    assert _calls(hass) == [("switch", "turn_off", {"entity_id": "switch.old"})]
    assert not manager._pending_off


@pytest.mark.asyncio
async def test_released_device_taken_over_by_another_room_is_not_switched_off():
    states = {"switch.dryer": "on", "switch.other": "on"}
    manager, hass = _multi_state_manager(states)
    await manager.evaluate(_room("switch.dryer"), 22, 55, 15)
    states["switch.dryer"] = "unavailable"
    await manager.evaluate(_room("switch.other"), 22, 55, 15)
    states["switch.dryer"] = "on"
    rooms = {"bathroom": _room("switch.other"), "cellar": _room("switch.dryer", area_id="cellar")}
    await manager.async_retry_pending_off(rooms)  # runs before the rooms, the cellar not evaluated yet
    await manager.evaluate(rooms["cellar"], 22, 55, 15)
    assert ("switch", "turn_off", {"entity_id": "switch.dryer"}) not in _calls(hass)
    assert not manager._pending_off


@pytest.mark.asyncio
async def test_climate_control_off_sends_nothing():
    manager, hass = _multi_state_manager({"switch.dryer": "off"})
    await manager.evaluate(_room("switch.dryer"), 22, 80, 15, control_active=False)
    await manager.evaluate(_room("switch.dryer", dehumidifier_enabled=False), 22, 80, 15, control_active=False)
    assert not _calls(hass)
    await manager.evaluate(_room("switch.dryer"), 22, 80, 15)
    assert _calls(hass) == [("switch", "turn_on", {"entity_id": "switch.dryer"})]


@pytest.mark.asyncio
async def test_short_humidity_dropout_holds_last_value():
    manager, hass = _multi_state_manager({"switch.dryer": "on"})
    with patch("custom_components.roommind.managers.dehumidifier_manager.time.monotonic", return_value=1000):
        await manager.evaluate(_room("switch.dryer"), 22, 55, 15)
    with patch("custom_components.roommind.managers.dehumidifier_manager.time.monotonic", return_value=1060):
        await manager.evaluate(_room("switch.dryer"), 22, None, 15)
    assert not _calls(hass)
    with patch("custom_components.roommind.managers.dehumidifier_manager.time.monotonic", return_value=1400):
        await manager.evaluate(_room("switch.dryer"), 22, None, 15)
    assert _calls(hass) == [("switch", "turn_off", {"entity_id": "switch.dryer"})]
