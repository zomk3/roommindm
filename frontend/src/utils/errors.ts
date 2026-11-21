import type { HomeAssistant } from "../types";
import { localize, type TranslationKey } from "./localize";

/** RoomMind and Home Assistant error codes with a message of their own. */
const CODE_KEYS: Record<string, TranslationKey> = {
  "3": "error.connection_lost",
  timeout: "error.timeout",
  unauthorized: "error.unauthorized",
  not_found: "error.not_found",
  invalid_format: "error.invalid_format",
  no_coordinator: "error.no_coordinator",
  no_model: "error.no_model",
  invalid_entity: "error.invalid_entity",
  duplicate_entity: "error.duplicate_entity",
  duplicate_group_id: "error.duplicate_group_id",
  invalid_member: "error.invalid_member",
  duplicate_member: "error.duplicate_member",
  invalid_master_entity: "error.invalid_master_entity",
  master_in_members: "error.master_in_members",
  master_is_other_member: "error.master_is_other_member",
  duplicate_master: "error.duplicate_master",
  invalid_action_script: "error.invalid_action_script",
  schedule_no_entity: "error.schedule_no_entity",
};

interface ErrorFields {
  code?: string | number;
  message?: string;
  /** Set by RoomMind for errors with an entry in strings.json `exceptions`. */
  translation_key?: string;
  translation_placeholders?: Record<string, string>;
}

interface ErrorLike extends ErrorFields {
  error?: ErrorFields;
}

const WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];

let backendHass: HomeAssistant | undefined;
let loadedLanguage: string | undefined;

/**
 * Make RoomMind's backend error translations available to errorText. Call with every new
 * `hass`: localize is replaced when translations load, the load itself runs once per language.
 */
export function useBackendErrors(hass: HomeAssistant): void {
  backendHass = hass;
  if (!hass.loadBackendTranslation || loadedLanguage === hass.language) return;
  loadedLanguage = hass.language;
  hass.loadBackendTranslation("exceptions", "roommind").catch(() => {
    loadedLanguage = undefined;
  });
}

/** The weekday key the backend sends as `day`, named in the UI language. */
function weekdayName(day: string, language: string): string {
  const index = WEEKDAYS.indexOf(day);
  if (index < 0) return day;
  // 2024-01-01 was a Monday
  return new Date(Date.UTC(2024, 0, 1 + index)).toLocaleDateString(language, {
    weekday: "long",
    timeZone: "UTC",
  });
}

function backendText(e: ErrorFields, language: string): string | undefined {
  if (!e.translation_key || !backendHass?.localize) return undefined;
  const values = { ...(e.translation_placeholders ?? {}) };
  if (values.day) values.day = weekdayName(values.day, language);
  const text = backendHass.localize(
    `component.roommind.exceptions.${e.translation_key}.message`,
    values,
  );
  return text || undefined;
}

/** Error the panel throws itself; `code` picks the message like a backend code. */
export class CodedError extends Error {
  constructor(
    public readonly code: string,
    message = code,
  ) {
    super(message);
  }
}

/**
 * Text for a failed call. `hass.callWS` rejects with `{ code, message }` (no Error), a lost
 * connection with the bare number 3 or a result object carrying `error`. A RoomMind
 * translation key (see useBackendErrors) wins, then known codes get a localized message,
 * else the message the call brought, else `fallback`.
 */
export function errorText(err: unknown, fallback: string, language: string): string {
  if (err === 3) return localize("error.connection_lost", language);
  const e = (err ?? {}) as ErrorLike;
  const translated =
    backendText(e, language) ?? (e.error ? backendText(e.error, language) : undefined);
  if (translated) return translated;
  const code = e.code ?? e.error?.code;
  const key = code !== undefined ? CODE_KEYS[String(code)] : undefined;
  if (key) return localize(key, language);
  const message = e.message ?? e.error?.message;
  return typeof message === "string" && message ? message : fallback;
}
