"""Per-room dehumidifier control using mold risk and humidity hysteresis.

Decision order each cycle, for a room whose climate control is on and whose
dehumidifier is enabled:

1. Humidity reading lost (after a short hold) or invalid bounds -> off at once.
2. Water tank full -> no commands (the device has stopped itself); notify.
3. Hysteresis: on at the upper bound or on mold risk, off at the lower bound,
   inside the band keep the current state.
4. Window open or quiet hours -> off (quiet hours yield to critical mold risk).
5. Outdoor air much drier and the room has a window sensor -> recommend airing
   (notification); with "prefer airing" hold a start back for a while (not for
   critical mold risk).
6. The switch happens once its condition has held for the switching delay, and
   never before the compressor's minimum run / pause time.
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass
from datetime import datetime
from datetime import time as dt_time

from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from ..const import (
    DEFAULT_DEHUMIDIFIER_DELAY_MINUTES,
    DEFAULT_DEHUMIDIFIER_MIN_OFF_MINUTES,
    DEFAULT_DEHUMIDIFIER_MIN_ON_MINUTES,
    DEFAULT_DEHUMIDIFIER_QUIET_END,
    DEFAULT_DEHUMIDIFIER_QUIET_START,
    DEFAULT_MOLD_F_RSI,
    VENTILATION_ABS_HUMIDITY_MARGIN,
    VENTILATION_NOTIFY_COOLDOWN_MINUTES,
    VENTILATION_PREFER_MINUTES,
)
from ..utils.mold_utils import absolute_humidity, calculate_mold_risk
from ..utils.notification_utils import (
    NotificationThrottler,
    async_send_mold_notification,
    dismiss_mold_notification,
)

_LOGGER = logging.getLogger(__name__)

DEHUMIDIFIER_DOMAINS = ("switch", "humidifier")
# A humidity sensor dropping out for a cycle or two must not short-cycle a compressor
HUMIDITY_HOLD_SECONDS = 300
# Longest gap counted as runtime between two cycles (a stalled loop is not runtime)
MAX_RUNTIME_STEP_SECONDS = 300

STATUS_OFF = "off"  # not controlled by RoomMind
STATUS_IDLE = "idle"
STATUS_RUNNING = "running"
STATUS_TANK_FULL = "tank_full"
STATUS_WINDOW = "window"
STATUS_QUIET = "quiet"


@dataclass
class DehumidifierStats:
    """Today's runtime of a room's dehumidifier."""

    day: str = ""
    runtime_s: float = 0.0
    last_ts: float | None = None


def _parse_hhmm(value: str, fallback: str) -> dt_time:
    for raw in (value, fallback):
        try:
            hours, minutes = str(raw).split(":")[:2]
            return dt_time(int(hours), int(minutes))
        except (ValueError, TypeError):
            continue
    return dt_time(0, 0)


def in_quiet_hours(now: datetime, start: str, end: str) -> bool:
    """Whether local *now* lies in [start, end); a window across midnight wraps."""
    t_start = _parse_hhmm(start, DEFAULT_DEHUMIDIFIER_QUIET_START)
    t_end = _parse_hhmm(end, DEFAULT_DEHUMIDIFIER_QUIET_END)
    current = now.time().replace(second=0, microsecond=0)
    if t_start == t_end:
        return False
    if t_start < t_end:
        return t_start <= current < t_end
    return current >= t_start or current < t_end


class DehumidifierManager:
    """Control switch and humidifier entities; runs alongside mold-prevention heating."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._entities: dict[str, str] = {}
        # Released devices that could not be switched off yet (unavailable at release)
        self._pending_off: set[str] = set()
        self._last_humidity: dict[str, tuple[float, float]] = {}
        # First cycle of a room in this run, while it has had no humidity reading yet: right
        # after a restart the sensor reports unknown for a while, which is not a sensor loss
        self._awaiting_first_reading: dict[str, float] = {}
        # Devices whose own target RoomMind already lowered in their current run
        self._target_lowered: set[str] = set()
        # Rooms whose climate control is off: RoomMind leaves their device alone (#36)
        self._paused: set[str] = set()
        # Switch waiting for its condition to hold for the delay: area -> (turn on?, since)
        self._pending: dict[str, tuple[bool, float]] = {}
        self._status: dict[str, str] = {}
        # Airing recommended since (monotonic), and the room's indoor/outdoor water content
        self._ventilate_since: dict[str, float] = {}
        self._ventilation: dict[str, tuple[float, float]] = {}
        self._tank_full: set[str] = set()
        self._stats: dict[str, DehumidifierStats] = {}
        self._throttler = NotificationThrottler()

    # --- device access -------------------------------------------------------------

    def _reachable(self, entity_id: str) -> bool:
        state = self.hass.states.get(entity_id)
        return state is not None and state.state not in ("unknown", "unavailable")

    async def _set_state(self, entity_id: str, active: bool) -> bool:
        if not self._reachable(entity_id):
            return False
        target = "on" if active else "off"
        if self.hass.states.get(entity_id).state == target:
            return True
        try:
            await self.hass.services.async_call(
                entity_id.split(".", maxsplit=1)[0], f"turn_{target}", {"entity_id": entity_id}, blocking=True
            )
        except HomeAssistantError:
            _LOGGER.exception("Could not set dehumidifier %s to %s", entity_id, target)
            return False
        return True

    async def _ensure_min_target(self, entity_id: str, device_target: float | None = None) -> None:
        """Keep a humidifier entity's own target low while RoomMind runs it.

        Its built-in humidistat (often a poor sensor next to the unit) would otherwise
        switch it off before the room reaches RoomMind's lower bound. *device_target* is the
        room's setting: None = the device's reported minimum (some report a lower one than
        they accept), 0 = leave the device's target alone. Tried once per run: a device that
        puts its target back is not sent the same command every cycle.
        """
        if device_target == 0:
            return
        if not entity_id.startswith("humidifier."):
            return
        state = self.hass.states.get(entity_id)
        if state is None or state.state != "on":
            self._target_lowered.discard(entity_id)  # try again in the next run
            return
        if entity_id in self._target_lowered:
            return  # once per run: some devices put their own target back (e.g. in auto mode)
        target = state.attributes.get("humidity")
        wanted = device_target if device_target is not None else state.attributes.get("min_humidity")
        if not isinstance(target, (int, float)) or not isinstance(wanted, (int, float)) or target <= wanted:
            return  # unknown, or already at or below the wanted target (never raised)
        self._target_lowered.add(entity_id)
        try:
            await self.hass.services.async_call(
                "humidifier", "set_humidity", {"entity_id": entity_id, "humidity": wanted}, blocking=True
            )
        except HomeAssistantError:
            _LOGGER.warning("Could not set the target humidity of %s to %s", entity_id, wanted)

    # --- read-only state for the room view ------------------------------------------

    def is_running(self, area_id: str) -> bool:
        """Whether RoomMind controls this room's dehumidifier right now and it is on."""
        entity = self._entities.get(area_id)
        if not entity or area_id in self._paused:
            return False
        state = self.hass.states.get(entity)
        return state is not None and state.state == "on"

    def status(self, area_id: str) -> str:
        """Why the room's dehumidifier is in its state (STATUS_*)."""
        if area_id not in self._entities or area_id in self._paused:
            return STATUS_OFF
        if self.is_running(area_id):
            return STATUS_RUNNING
        return self._status.get(area_id, STATUS_IDLE)

    def ventilation(self, area_id: str) -> tuple[float, float] | None:
        """(indoor, outdoor) water content in g/m³ while airing is recommended, else None."""
        return self._ventilation.get(area_id) if area_id in self._ventilate_since else None

    def stats(self, area_id: str) -> DehumidifierStats:
        stats = self._stats.get(area_id)
        if stats is None or stats.day != dt_util.now().date().isoformat():
            return DehumidifierStats()
        return stats

    def needs_heat_fallback(self, room: dict) -> bool:
        """The room's dehumidifier is enabled but cannot work: mold-prevention heat must step in."""
        entity = room.get("dehumidifier_entity", "")
        if not room.get("dehumidifier_enabled", False) or not entity:
            return False
        if not self._reachable(entity):
            return True
        tank = room.get("dehumidifier_tank_sensor", "")
        tank_state = self.hass.states.get(tank) if tank else None
        return tank_state is not None and tank_state.state == "on"

    # --- lifecycle -------------------------------------------------------------------

    async def remove_room(self, area_id: str) -> None:
        """Release a room's device, switching it off now or as soon as it is reachable again."""
        self._last_humidity.pop(area_id, None)
        self._awaiting_first_reading.pop(area_id, None)
        self._paused.discard(area_id)
        self._pending.pop(area_id, None)
        self._status.pop(area_id, None)
        self._clear_ventilation(area_id)
        self._clear_tank(area_id)
        entity = self._entities.pop(area_id, None)
        if entity and not await self._set_state(entity, False):
            _LOGGER.warning("Dehumidifier %s unreachable on release, switching it off once it is back", entity)
            self._pending_off.add(entity)

    async def async_retry_pending_off(self, rooms: dict[str, dict]) -> None:
        """Once per cycle: switch off released devices that are back and no room claims anymore."""
        if not self._pending_off:
            return
        claimed = {
            room.get("dehumidifier_entity")
            for room in rooms.values()
            if room.get("dehumidifier_enabled") and not room.get("is_outdoor", False)
        }
        for entity in list(self._pending_off):
            if entity in claimed:
                self._pending_off.discard(entity)  # another room controls it now
            elif await self._set_state(entity, False):
                self._pending_off.discard(entity)

    def _still_starting(self, area_id: str) -> bool:
        """No humidity reading for the room yet in this run, and less than the hold time passed."""
        if area_id in self._last_humidity or self._awaiting_first_reading.get(area_id) == -math.inf:
            return False
        started = self._awaiting_first_reading.setdefault(area_id, time.monotonic())
        return time.monotonic() - started <= HUMIDITY_HOLD_SECONDS

    def _held_humidity(self, area_id: str, humidity: float | None) -> float | None:
        now = time.monotonic()
        if humidity is not None and math.isfinite(humidity) and 0 <= humidity <= 100:
            self._last_humidity[area_id] = (humidity, now)
            self._awaiting_first_reading[area_id] = -math.inf  # the start phase is over
            return humidity
        last = self._last_humidity.get(area_id)
        if last and now - last[1] <= HUMIDITY_HOLD_SECONDS:
            return last[0]
        self._last_humidity.pop(area_id, None)
        return None

    # --- the cycle -------------------------------------------------------------------

    async def evaluate(
        self,
        room: dict,
        temperature: float | None,
        humidity: float | None,
        outdoor_temp: float | None,
        settings: dict | None = None,
        *,
        control_active: bool = True,
        window_open: bool = False,
        outdoor_humidity: float | None = None,
        area_name: str | None = None,
    ) -> None:
        """Run one control cycle for a room's dehumidifier (see the module docstring).

        Climate control off sends no commands at all (#36); the room is picked up again
        once control is back on. Losing the humidity reading (after the hold), disabling,
        swapping or removing act at once.
        """
        settings = settings or {}
        area_id = room.get("area_id", "unknown")
        if not control_active:
            self._paused.add(area_id)
            self._pending.pop(area_id, None)
            return
        self._paused.discard(area_id)
        entity = room.get("dehumidifier_entity", "")
        enabled = room.get("dehumidifier_enabled", False) and not room.get("is_outdoor", False)
        previous = self._entities.get(area_id)
        if previous and (previous != entity or not enabled):
            await self.remove_room(area_id)
        if not enabled or not entity or entity.split(".")[0] not in DEHUMIDIFIER_DOMAINS:
            return
        self._entities[area_id] = entity
        self._pending_off.discard(entity)
        self._track_stats(area_id, entity)
        name = area_name or area_id

        lower = room.get("dehumidifier_lower_bound", 50)
        upper = room.get("dehumidifier_upper_bound", 60)
        humidity = self._held_humidity(area_id, humidity)
        if humidity is None and self._still_starting(area_id):
            self._status[area_id] = STATUS_IDLE
            return  # leave the device as it is until the sensor reports after a restart
        if humidity is None or not 0 < lower < upper <= 100:
            self._pending.pop(area_id, None)
            self._status[area_id] = STATUS_IDLE
            self._clear_ventilation(area_id)
            await self._set_state(entity, False)
            return

        if await self._handle_tank(area_id, name, room.get("dehumidifier_tank_sensor", ""), settings):
            self._pending.pop(area_id, None)
            self._status[area_id] = STATUS_TANK_FULL
            return

        risk = "ok"
        if temperature is not None and math.isfinite(temperature):
            risk, _, _ = calculate_mold_risk(
                temperature, humidity, outdoor_temp, f_rsi=settings.get("mold_f_rsi", DEFAULT_MOLD_F_RSI)
            )
        critical = risk == "critical"
        wants_drying = humidity >= upper or risk in ("warning", "critical")
        desired: bool | None = False if humidity <= lower else (True if wants_drying else None)
        self._status[area_id] = STATUS_IDLE

        await self._handle_ventilation(
            area_id,
            name,
            temperature,
            humidity,
            outdoor_temp,
            outdoor_humidity,
            wants_drying,
            window_open,
            bool(room.get("window_sensors")),
            settings,
        )

        # Window and quiet hours are not humidity noise: they skip the switching delay
        # (windows have their own open delay per room), not the compressor protection
        use_delay = True
        if window_open:
            desired, use_delay = False, False
            self._status[area_id] = STATUS_WINDOW
        elif (
            not critical
            and settings.get("dehumidifier_quiet_enabled", False)
            and in_quiet_hours(
                dt_util.now(),
                settings.get("dehumidifier_quiet_start", DEFAULT_DEHUMIDIFIER_QUIET_START),
                settings.get("dehumidifier_quiet_end", DEFAULT_DEHUMIDIFIER_QUIET_END),
            )
        ):
            desired, use_delay = False, False
            self._status[area_id] = STATUS_QUIET
        elif desired is True and not critical and settings.get("dehumidifier_prefer_ventilation", False):
            since = self._ventilate_since.get(area_id)
            if since is not None and time.monotonic() - since < VENTILATION_PREFER_MINUTES * 60:
                desired = None  # give airing a chance first; a running device keeps running

        if desired is None:
            self._pending.pop(area_id, None)  # inside the band: the condition was interrupted
        else:
            await self._switch_after_delay(area_id, entity, desired, settings, use_delay=use_delay)
        await self._ensure_min_target(entity, room.get("dehumidifier_device_target"))

    async def _switch_after_delay(
        self, area_id: str, entity: str, active: bool, settings: dict, *, use_delay: bool = True
    ) -> None:
        state = self.hass.states.get(entity)
        if state is not None and state.state == ("on" if active else "off"):
            self._pending.pop(area_id, None)  # already there
            return
        now = time.monotonic()
        pending = self._pending.get(area_id)
        if pending is None or pending[0] != active:
            self._pending[area_id] = pending = (active, now)
        delay = settings.get("dehumidifier_delay_minutes", DEFAULT_DEHUMIDIFIER_DELAY_MINUTES) * 60 if use_delay else 0
        if now - pending[1] < delay or not self._compressor_allows(state, active, settings):
            return
        self._pending.pop(area_id, None)
        await self._set_state(entity, active)

    def _compressor_allows(self, state: State | None, active: bool, settings: dict) -> bool:
        """Minimum run before switching off, minimum pause before switching on.

        Measured from the device's last real state change, whoever caused it.
        """
        changed = getattr(state, "last_changed", None)
        if not isinstance(changed, datetime):
            return True
        key, default = (
            ("dehumidifier_min_off_minutes", DEFAULT_DEHUMIDIFIER_MIN_OFF_MINUTES)
            if active
            else ("dehumidifier_min_on_minutes", DEFAULT_DEHUMIDIFIER_MIN_ON_MINUTES)
        )
        minimum_s = float(settings.get(key, default)) * 60
        return bool((dt_util.utcnow() - changed).total_seconds() >= minimum_s)

    # --- tank, airing, runtime ---------------------------------------------------

    async def _handle_tank(self, area_id: str, name: str, tank_sensor: str, settings: dict) -> bool:
        tank = self.hass.states.get(tank_sensor) if tank_sensor else None
        if tank is None or tank.state != "on":
            self._clear_tank(area_id)
            return False
        if area_id not in self._tank_full:
            self._tank_full.add(area_id)
            if settings.get("mold_notifications_enabled", True):
                await async_send_mold_notification(
                    self.hass,
                    area_id,
                    name,
                    settings.get("mold_notification_targets", []),
                    message=f"The dehumidifier in {name} has stopped: its water tank is full.",
                    title="RoomMind: Dehumidifier tank full",
                    tag_suffix="tank",
                )
        return True

    def _clear_tank(self, area_id: str) -> None:
        if area_id in self._tank_full:
            self._tank_full.discard(area_id)
            dismiss_mold_notification(self.hass, area_id, "tank")

    async def _handle_ventilation(
        self,
        area_id: str,
        name: str,
        temperature: float | None,
        humidity: float,
        outdoor_temp: float | None,
        outdoor_humidity: float | None,
        wants_drying: bool,
        window_open: bool,
        has_window: bool,
        settings: dict,
    ) -> None:
        """Recommend airing while the room needs drying and outdoor air holds clearly less water.

        Only for rooms with a window sensor: a room without one may have no window to open,
        and RoomMind could not tell that the advice was followed.
        """
        if (
            not has_window
            or window_open
            or not wants_drying
            or temperature is None
            or outdoor_temp is None
            or outdoor_humidity is None
            or not all(math.isfinite(v) for v in (temperature, outdoor_temp, outdoor_humidity))
        ):
            self._clear_ventilation(area_id)
            return
        indoor = absolute_humidity(temperature, humidity)
        outdoor = absolute_humidity(outdoor_temp, outdoor_humidity)
        if indoor - outdoor < VENTILATION_ABS_HUMIDITY_MARGIN:
            self._clear_ventilation(area_id)
            return
        self._ventilation[area_id] = (round(indoor, 1), round(outdoor, 1))
        self._ventilate_since.setdefault(area_id, time.monotonic())
        key = f"ventilate_{area_id}"
        if (
            settings.get("dehumidifier_ventilation_notify", True)
            and settings.get("mold_notifications_enabled", True)
            and self._throttler.should_send(key, VENTILATION_NOTIFY_COOLDOWN_MINUTES * 60)
        ):
            await async_send_mold_notification(
                self.hass,
                area_id,
                name,
                settings.get("mold_notification_targets", []),
                message=(
                    f"Airing dries {name} faster than the dehumidifier: outdoor air holds "
                    f"{outdoor:.1f} g/m³ of water, indoor air {indoor:.1f} g/m³. Open a window for 5-10 minutes."
                ),
                title="RoomMind: Air the room",
                tag_suffix="ventilate",
            )
            self._throttler.record_sent(key)

    def _clear_ventilation(self, area_id: str) -> None:
        self._ventilation.pop(area_id, None)
        if self._ventilate_since.pop(area_id, None) is not None:
            dismiss_mold_notification(self.hass, area_id, "ventilate")
            self._throttler.clear(f"ventilate_{area_id}")

    def _track_stats(self, area_id: str, entity: str) -> None:
        today = dt_util.now().date().isoformat()
        stats = self._stats.get(area_id)
        if stats is None or stats.day != today:
            stats = self._stats[area_id] = DehumidifierStats(day=today)
        now = time.monotonic()
        step = 0.0 if stats.last_ts is None else min(now - stats.last_ts, MAX_RUNTIME_STEP_SECONDS)
        stats.last_ts = now
        state = self.hass.states.get(entity)
        if step <= 0 or state is None or state.state != "on":
            return
        stats.runtime_s += step
