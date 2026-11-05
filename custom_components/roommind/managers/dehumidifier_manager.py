"""Per-room dehumidifier control using mold risk and humidity hysteresis."""

from __future__ import annotations

import logging
import math
import time

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from ..const import DEFAULT_MOLD_F_RSI
from ..utils.mold_utils import calculate_mold_risk

_LOGGER = logging.getLogger(__name__)

DEHUMIDIFIER_DOMAINS = ("switch", "humidifier")
# A humidity sensor dropping out for a cycle or two must not short-cycle a compressor
HUMIDITY_HOLD_SECONDS = 300


class DehumidifierManager:
    """Control switch and humidifier entities; runs alongside mold-prevention heating."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._entities: dict[str, str] = {}
        # Released devices that could not be switched off yet (unavailable at release)
        self._pending_off: set[str] = set()
        self._last_humidity: dict[str, tuple[float, float]] = {}

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

    async def remove_room(self, area_id: str) -> None:
        """Release a room's device, switching it off now or as soon as it is reachable again."""
        self._last_humidity.pop(area_id, None)
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

    def _held_humidity(self, area_id: str, humidity: float | None) -> float | None:
        now = time.monotonic()
        if humidity is not None and math.isfinite(humidity) and 0 <= humidity <= 100:
            self._last_humidity[area_id] = (humidity, now)
            return humidity
        last = self._last_humidity.get(area_id)
        if last and now - last[1] <= HUMIDITY_HOLD_SECONDS:
            return last[0]
        self._last_humidity.pop(area_id, None)
        return None

    async def evaluate(
        self,
        room: dict,
        temperature: float | None,
        humidity: float | None,
        outdoor_temp: float | None,
        f_rsi: float = DEFAULT_MOLD_F_RSI,
        control_active: bool = True,
    ) -> None:
        """Start on upper bound or mold risk; stop at lower bound or invalid sensors.

        Climate control off sends no commands at all (#36); the room is picked up again
        once control is back on.
        """
        if not control_active:
            return
        area_id = room.get("area_id", "unknown")
        entity = room.get("dehumidifier_entity", "")
        enabled = room.get("dehumidifier_enabled", False) and not room.get("is_outdoor", False)
        previous = self._entities.get(area_id)
        if previous and (previous != entity or not enabled):
            await self.remove_room(area_id)
        if not enabled or not entity or entity.split(".")[0] not in DEHUMIDIFIER_DOMAINS:
            return
        self._entities[area_id] = entity
        self._pending_off.discard(entity)
        lower = room.get("dehumidifier_lower_bound", 50)
        upper = room.get("dehumidifier_upper_bound", 60)
        humidity = self._held_humidity(area_id, humidity)
        if humidity is None or not 0 < lower < upper <= 100:
            await self._set_state(entity, False)
            return
        if humidity <= lower:
            await self._set_state(entity, False)
            return
        risk = "ok"
        if temperature is not None and math.isfinite(temperature):
            risk, _, _ = calculate_mold_risk(temperature, humidity, outdoor_temp, f_rsi=f_rsi)
        if humidity >= upper or risk in ("warning", "critical"):
            await self._set_state(entity, True)
