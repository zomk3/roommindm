import type { HomeAssistant } from "../types";

/**
 * An entity of the dehumidifier's own device, recognised by domain and name
 * (tank-full binary sensor). Empty when none fits.
 */
export function findDeviceSibling(
  hass: HomeAssistant,
  entityId: string,
  domain: "binary_sensor" | "sensor",
  pattern: RegExp,
): string {
  const deviceId = hass.entities?.[entityId]?.device_id;
  if (!deviceId) return "";
  const match = Object.values(hass.entities).find(
    (e) =>
      e.device_id === deviceId && e.entity_id.startsWith(`${domain}.`) && pattern.test(e.entity_id),
  );
  return match?.entity_id ?? "";
}

export const TANK_PATTERN = /tank|water|wasser|full|voll|bucket/;

/** "2 h 5 min" / "45 min" for today's runtime. */
export function formatRuntime(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  return h > 0 ? `${h} h ${m} min` : `${m} min`;
}
