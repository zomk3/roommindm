"""Per-room dehumidifier control using mold risk and humidity hysteresis."""

from __future__ import annotations

import logging
import math

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from ..utils.mold_utils import calculate_mold_risk

_LOGGER = logging.getLogger(__name__)


class DehumidifierManager:
    """Control switch and humidifier entities without raising heat targets."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._entities: dict[str, str] = {}

    async def _set_state(self, entity_id: str, active: bool) -> bool:
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unknown", "unavailable"):
            return False
        target = "on" if active else "off"
        if state.state == target:
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
        """Turn off a previously controlled device before releasing it."""
        entity = self._entities.get(area_id)
        if entity and await self._set_state(entity, False):
            self._entities.pop(area_id, None)

    async def evaluate(
        self, room: dict, temperature: float | None, humidity: float | None, outdoor_temp: float | None
    ) -> None:
        """Start on upper bound or mold risk; stop at lower bound or invalid sensors."""
        area_id = room.get("area_id", "unknown")
        entity = room.get("dehumidifier_entity", "")
        enabled = room.get("dehumidifier_enabled", False) and not room.get("is_outdoor", False)
        previous = self._entities.get(area_id)
        if previous and (previous != entity or not enabled):
            await self.remove_room(area_id)
            if area_id in self._entities:
                return
        if not enabled or not entity or entity.split(".")[0] not in ("switch", "humidifier"):
            return
        self._entities[area_id] = entity
        lower = room.get("dehumidifier_lower_bound", 50)
        upper = room.get("dehumidifier_upper_bound", 60)
        if humidity is None or not math.isfinite(humidity) or not 0 <= humidity <= 100 or not 0 < lower < upper <= 100:
            await self._set_state(entity, False)
            return
        if humidity <= lower:
            await self._set_state(entity, False)
            return
        risk = "ok"
        if temperature is not None and math.isfinite(temperature):
            risk, _ = calculate_mold_risk(temperature, humidity, outdoor_temp)
        if humidity >= upper or risk in ("warning", "critical"):
            await self._set_state(entity, True)
