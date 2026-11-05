"""Dehumidifier extras: device target, window, tank, compressor protection, airing, quiet hours, runtime."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.roommind.managers.dehumidifier_manager import (
    STATUS_QUIET,
    STATUS_RUNNING,
    STATUS_TANK_FULL,
    STATUS_WINDOW,
    DehumidifierManager,
    in_quiet_hours,
)

MOD = "custom_components.roommind.managers.dehumidifier_manager"
IMMEDIATE = {"dehumidifier_delay_minutes": 0, "dehumidifier_min_on_minutes": 0, "dehumidifier_min_off_minutes": 0}
NOW = datetime(2026, 11, 5, 21, 0, tzinfo=UTC)


def _manager(states: dict):
    """states: entity_id -> state str, or (state, attributes) / (state, attributes, last_changed)."""

    def get(eid):
        if eid not in states:
            return None
        value = states[eid]
        if isinstance(value, str):
            value = (value,)
        state, attrs, changed = (*value, {}, None)[:3] if len(value) == 1 else (*value, None)[:3]
        return SimpleNamespace(state=state, attributes=attrs or {}, last_changed=changed)

    hass = MagicMock()
    hass.states.get.side_effect = get
    hass.services.async_call = AsyncMock()
    return DehumidifierManager(hass), hass


def _room(entity="switch.dryer", **extra) -> dict:
    return {
        "area_id": "bath",
        "dehumidifier_enabled": True,
        "dehumidifier_entity": entity,
        "dehumidifier_lower_bound": 50,
        "dehumidifier_upper_bound": 60,
        **extra,
    }


def _calls(hass) -> list[tuple]:
    return [c.args[:3] for c in hass.services.async_call.await_args_list]


# --- 1. the device's own target ---------------------------------------------------------


@pytest.mark.asyncio
async def test_running_humidifier_gets_its_minimum_target():
    eid = "humidifier.dryer"
    manager, hass = _manager({eid: ("on", {"humidity": 50, "min_humidity": 25})})
    await manager.evaluate(_room(eid), 22, 55, 15, IMMEDIATE)
    assert _calls(hass) == [("humidifier", "set_humidity", {"entity_id": eid, "humidity": 25})]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("eid", "state"),
    [
        ("humidifier.dryer", ("on", {"humidity": 25, "min_humidity": 25})),  # already there
        ("humidifier.dryer", ("off", {"humidity": 50, "min_humidity": 25})),  # not running
        ("humidifier.dryer", ("on", {"humidity": 50})),  # no minimum known
        ("switch.dryer", "on"),  # a plug has no target
    ],
)
async def test_no_target_change_when_not_needed(eid, state):
    manager, hass = _manager({eid: state})
    await manager.evaluate(_room(eid), 22, 55, 15, IMMEDIATE)
    assert _calls(hass) == []


# --- 2. window open -----------------------------------------------------------------------


@pytest.mark.asyncio
async def test_open_window_switches_off_without_the_switching_delay():
    states = {"switch.dryer": "on"}
    manager, hass = _manager(states)
    await manager.evaluate(_room(), 22, 70, 15, {"dehumidifier_delay_minutes": 10}, window_open=True)
    assert _calls(hass) == [("switch", "turn_off", {"entity_id": "switch.dryer"})]
    states["switch.dryer"] = "off"  # as the real device reports after the command
    assert manager.status("bath") == STATUS_WINDOW


@pytest.mark.asyncio
async def test_open_window_still_respects_the_minimum_run():
    manager, hass = _manager({"switch.dryer": ("on", {}, NOW - timedelta(minutes=3))})
    with patch(f"{MOD}.dt_util.utcnow", return_value=NOW):
        await manager.evaluate(_room(), 22, 70, 15, {"dehumidifier_min_on_minutes": 10}, window_open=True)
    assert _calls(hass) == []


# --- 3. water tank full -------------------------------------------------------------------


@pytest.mark.asyncio
async def test_full_tank_sends_nothing_notifies_once_and_clears():
    states = {"switch.dryer": "off", "binary_sensor.tank": "on"}
    manager, hass = _manager(states)
    room = _room(dehumidifier_tank_sensor="binary_sensor.tank")
    with (
        patch(f"{MOD}.async_send_mold_notification", new_callable=AsyncMock) as notify,
        patch(f"{MOD}.dismiss_mold_notification") as dismiss,
    ):
        await manager.evaluate(room, 22, 70, 15, IMMEDIATE)
        await manager.evaluate(room, 22, 70, 15, IMMEDIATE)
        assert _calls(hass) == []
        assert manager.status("bath") == STATUS_TANK_FULL
        assert notify.await_count == 1
        assert notify.await_args.kwargs["tag_suffix"] == "tank"
        states["binary_sensor.tank"] = "off"
        await manager.evaluate(room, 22, 70, 15, IMMEDIATE)
        dismiss.assert_called_once_with(hass, "bath", "tank")
    assert _calls(hass) == [("switch", "turn_on", {"entity_id": "switch.dryer"})]


@pytest.mark.parametrize(
    ("states", "room_extra", "expected"),
    [
        ({"switch.dryer": "on", "binary_sensor.tank": "on"}, {"dehumidifier_tank_sensor": "binary_sensor.tank"}, True),
        ({"switch.dryer": "unavailable"}, {}, True),
        (
            {"switch.dryer": "on", "binary_sensor.tank": "off"},
            {"dehumidifier_tank_sensor": "binary_sensor.tank"},
            False,
        ),
        ({"switch.dryer": "on"}, {}, False),
        ({"switch.dryer": "unavailable"}, {"dehumidifier_enabled": False}, False),
    ],
)
def test_heat_fallback_when_the_dehumidifier_cannot_work(states, room_extra, expected):
    manager, _ = _manager(states)
    assert manager.needs_heat_fallback(_room(**room_extra)) is expected


# --- 4. compressor protection -------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("state", "humidity", "minutes_ago", "switches"),
    [
        ("off", 70, 2, False),  # paused 2 of 5 minutes
        ("off", 70, 6, True),
        ("on", 45, 8, False),  # ran 8 of 10 minutes
        ("on", 45, 11, True),
    ],
)
async def test_minimum_run_and_pause(state, humidity, minutes_ago, switches):
    manager, hass = _manager({"switch.dryer": (state, {}, NOW - timedelta(minutes=minutes_ago))})
    settings = {"dehumidifier_delay_minutes": 0, "dehumidifier_min_on_minutes": 10, "dehumidifier_min_off_minutes": 5}
    with patch(f"{MOD}.dt_util.utcnow", return_value=NOW):
        await manager.evaluate(_room(), 22, humidity, 15, settings)
    assert bool(_calls(hass)) is switches


# --- 5. airing ----------------------------------------------------------------------------

WINDOW_ROOM = _room(window_sensors=["binary_sensor.bath_window"])


@pytest.mark.asyncio
async def test_drier_outdoor_air_recommends_airing_with_a_throttled_notification():
    manager, hass = _manager({"switch.dryer": "on"})
    with (
        patch(f"{MOD}.async_send_mold_notification", new_callable=AsyncMock) as notify,
        patch(f"{MOD}.dismiss_mold_notification") as dismiss,
    ):
        # 21 °C / 65 % indoors holds ~11.8 g/m³, 2 °C / 85 % outdoors ~4.7 g/m³
        await manager.evaluate(WINDOW_ROOM, 21, 65, 2, IMMEDIATE, outdoor_humidity=85)
        await manager.evaluate(WINDOW_ROOM, 21, 65, 2, IMMEDIATE, outdoor_humidity=85)
        indoor, outdoor = manager.ventilation("bath")
        assert indoor - outdoor > 6
        assert notify.await_count == 1
        assert notify.await_args.kwargs["tag_suffix"] == "ventilate"
        await manager.evaluate(WINDOW_ROOM, 21, 55, 2, IMMEDIATE, outdoor_humidity=85)  # dry enough now
        assert manager.ventilation("bath") is None
        dismiss.assert_called_once_with(hass, "bath", "ventilate")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("outdoor_temp", "outdoor_humidity", "window_open", "settings_extra"),
    [
        (25, 70, False, {}),  # humid summer air: no point airing
        (2, None, False, {}),  # no outdoor humidity sensor
        (2, 85, True, {}),  # already airing
    ],
)
async def test_no_airing_hint(outdoor_temp, outdoor_humidity, window_open, settings_extra):
    manager, _ = _manager({"switch.dryer": "on"})
    with patch(f"{MOD}.async_send_mold_notification", new_callable=AsyncMock) as notify:
        await manager.evaluate(
            WINDOW_ROOM,
            21,
            65,
            outdoor_temp,
            {**IMMEDIATE, **settings_extra},
            outdoor_humidity=outdoor_humidity,
            window_open=window_open,
        )
    assert manager.ventilation("bath") is None
    assert notify.await_count == 0


@pytest.mark.asyncio
async def test_airing_notification_can_be_switched_off():
    manager, _ = _manager({"switch.dryer": "on"})
    with patch(f"{MOD}.async_send_mold_notification", new_callable=AsyncMock) as notify:
        await manager.evaluate(
            WINDOW_ROOM, 21, 65, 2, {**IMMEDIATE, "dehumidifier_ventilation_notify": False}, outdoor_humidity=85
        )
    assert manager.ventilation("bath") is not None  # still shown in the panel
    assert notify.await_count == 0


@pytest.mark.asyncio
async def test_prefer_airing_holds_a_start_back_for_30_minutes():
    manager, hass = _manager({"switch.dryer": "off"})
    settings = {**IMMEDIATE, "dehumidifier_prefer_ventilation": True}
    # warning, not critical: critical risk skips the airing preference (tested below)
    with (
        patch(f"{MOD}.async_send_mold_notification", new_callable=AsyncMock),
        patch(f"{MOD}.calculate_mold_risk", return_value=("warning", 75, 15)),
    ):
        with patch(f"{MOD}.time.monotonic", return_value=0):
            await manager.evaluate(WINDOW_ROOM, 21, 65, 2, settings, outdoor_humidity=85)
        with patch(f"{MOD}.time.monotonic", return_value=29 * 60):
            await manager.evaluate(WINDOW_ROOM, 21, 65, 2, settings, outdoor_humidity=85)
        assert _calls(hass) == []
        with patch(f"{MOD}.time.monotonic", return_value=30 * 60):
            await manager.evaluate(WINDOW_ROOM, 21, 65, 2, settings, outdoor_humidity=85)
    assert _calls(hass) == [("switch", "turn_on", {"entity_id": "switch.dryer"})]


@pytest.mark.asyncio
async def test_prefer_airing_does_not_hold_back_on_critical_mold_risk():
    manager, hass = _manager({"switch.dryer": "off"})
    settings = {**IMMEDIATE, "dehumidifier_prefer_ventilation": True}
    with (
        patch(f"{MOD}.async_send_mold_notification", new_callable=AsyncMock),
        patch(f"{MOD}.calculate_mold_risk", return_value=("critical", 85, 12)),
    ):
        await manager.evaluate(WINDOW_ROOM, 21, 65, 2, settings, outdoor_humidity=85)
    assert _calls(hass) == [("switch", "turn_on", {"entity_id": "switch.dryer"})]


@pytest.mark.asyncio
async def test_no_airing_hint_without_a_window_sensor():
    manager, hass = _manager({"switch.dryer": "off"})
    settings = {**IMMEDIATE, "dehumidifier_prefer_ventilation": True}
    with (
        patch(f"{MOD}.async_send_mold_notification", new_callable=AsyncMock) as notify,
        patch(f"{MOD}.calculate_mold_risk", return_value=("warning", 75, 15)),
    ):
        await manager.evaluate(_room(), 21, 65, 2, settings, outdoor_humidity=85)
    assert manager.ventilation("bath") is None
    assert notify.await_count == 0
    # and "prefer airing" does not hold the dehumidifier back there
    assert _calls(hass) == [("switch", "turn_on", {"entity_id": "switch.dryer"})]


# --- 6. quiet hours -----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("hhmm", "start", "end", "expected"),
    [
        ("23:00", "22:00", "07:00", True),
        ("06:59", "22:00", "07:00", True),
        ("07:00", "22:00", "07:00", False),
        ("12:00", "22:00", "07:00", False),
        ("13:30", "13:00", "15:00", True),
        ("15:00", "13:00", "15:00", False),
        ("12:00", "12:00", "12:00", False),
        ("23:00", "bad", "07:00", True),  # falls back to 22:00
    ],
)
def test_in_quiet_hours(hhmm, start, end, expected):
    h, m = map(int, hhmm.split(":"))
    assert in_quiet_hours(datetime(2026, 11, 5, h, m), start, end) is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(("risk", "switches_off"), [("ok", True), ("critical", False)])
async def test_quiet_hours_switch_off_unless_mold_risk_is_critical(risk, switches_off):
    states = {"switch.dryer": "on"}
    manager, hass = _manager(states)
    settings = {**IMMEDIATE, "dehumidifier_quiet_enabled": True, "dehumidifier_delay_minutes": 10}
    with (
        patch(f"{MOD}.dt_util.now", return_value=datetime(2026, 11, 5, 23, 0)),
        patch(f"{MOD}.calculate_mold_risk", return_value=(risk, 85, 12)),
    ):
        await manager.evaluate(_room(), 22, 70, 15, settings)
    assert (_calls(hass) == [("switch", "turn_off", {"entity_id": "switch.dryer"})]) is switches_off
    if switches_off:
        states["switch.dryer"] = "off"  # as the real device reports after the command
        assert manager.status("bath") == STATUS_QUIET


# --- 7. runtime ----------------------------------------------------------------


@pytest.mark.asyncio
async def test_runtime_today():
    manager, _ = _manager({"switch.dryer": "on"})
    day = datetime(2026, 11, 5, 12, 0)
    with patch(f"{MOD}.dt_util.now", return_value=day):
        for t in (0, 60, 120, 180):  # 3 minutes on
            with patch(f"{MOD}.time.monotonic", return_value=t):
                await manager.evaluate(_room(), 22, 55, 15, IMMEDIATE)
        assert manager.stats("bath").runtime_s == 180
        assert manager.status("bath") == STATUS_RUNNING
    with patch(f"{MOD}.dt_util.now", return_value=day + timedelta(days=1)):
        assert manager.stats("bath").runtime_s == 0  # a new day starts at zero


@pytest.mark.asyncio
async def test_runtime_counts_only_while_on_and_caps_gaps():
    states = {"switch.dryer": "off"}
    manager, _ = _manager(states)
    with patch(f"{MOD}.dt_util.now", return_value=datetime(2026, 11, 5, 12, 0)):
        for t, state in ((0, "off"), (60, "off"), (120, "on"), (3600, "on")):
            states["switch.dryer"] = state
            with patch(f"{MOD}.time.monotonic", return_value=t):
                await manager.evaluate(_room(), 22, 55, 15, IMMEDIATE)
        assert manager.stats("bath").runtime_s == 60 + 300  # one minute, then a capped gap


# --- after a restart ----------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_switch_off_while_the_humidity_sensor_starts_up():
    manager, hass = _manager({"switch.dryer": "on"})
    for t in (0, 120, 300):  # the sensor reports unknown for a while after a restart
        with patch(f"{MOD}.time.monotonic", return_value=t):
            await manager.evaluate(_room(), 22, None, 15, IMMEDIATE)
    assert _calls(hass) == []
    with patch(f"{MOD}.time.monotonic", return_value=301):  # never reported: safety off
        await manager.evaluate(_room(), 22, None, 15, IMMEDIATE)
    assert _calls(hass) == [("switch", "turn_off", {"entity_id": "switch.dryer"})]


@pytest.mark.asyncio
async def test_start_phase_ends_with_the_first_reading():
    manager, hass = _manager({"switch.dryer": "on"})
    with patch(f"{MOD}.time.monotonic", return_value=0):
        await manager.evaluate(_room(), 22, None, 15, IMMEDIATE)
    with patch(f"{MOD}.time.monotonic", return_value=10):
        await manager.evaluate(_room(), 22, 55, 15, IMMEDIATE)
    with patch(f"{MOD}.time.monotonic", return_value=400):  # a later loss is a real loss
        await manager.evaluate(_room(), 22, None, 15, IMMEDIATE)
    assert _calls(hass) == [("switch", "turn_off", {"entity_id": "switch.dryer"})]


# --- device target, once per run ----------------------------------------------------------


@pytest.mark.asyncio
async def test_device_target_is_lowered_once_per_run_even_if_the_device_puts_it_back():
    eid = "humidifier.dryer"
    states = {eid: ("on", {"humidity": 50, "min_humidity": 25})}
    manager, hass = _manager(states)
    for _ in range(4):  # the device keeps reporting 50 % (e.g. in auto mode)
        await manager.evaluate(_room(eid), 22, 55, 15, IMMEDIATE)
    assert _calls(hass) == [("humidifier", "set_humidity", {"entity_id": eid, "humidity": 25})]
    states[eid] = ("off", {"humidity": 50, "min_humidity": 25})
    await manager.evaluate(_room(eid), 22, 55, 15, IMMEDIATE)
    states[eid] = ("on", {"humidity": 50, "min_humidity": 25})
    await manager.evaluate(_room(eid), 22, 55, 15, IMMEDIATE)
    assert _calls(hass).count(("humidifier", "set_humidity", {"entity_id": eid, "humidity": 25})) == 2
