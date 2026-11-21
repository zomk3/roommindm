import { describe, expect, test } from "vitest";
import type { HomeAssistant } from "../types";
import { errorText, useBackendErrors } from "./errors";

function hassWith(translations: Record<string, string>, language = "de"): HomeAssistant {
  return {
    language,
    loadBackendTranslation: () => Promise.resolve(),
    localize: (key: string, values?: Record<string, string | number>) =>
      (translations[key] ?? "").replace(/\{(\w+)\}/g, (_, name: string) =>
        String(values?.[name] ?? ""),
      ),
  } as unknown as HomeAssistant;
}

describe("errorText", () => {
  test("a RoomMind translation key wins over the English message", () => {
    useBackendErrors(
      hassWith({
        "component.roommind.exceptions.room_not_found.message": "Raum {area_id} nicht gefunden.",
      }),
    );
    const err = {
      code: "not_found",
      message: "Room 'bad' not found",
      translation_key: "room_not_found",
      translation_placeholders: { area_id: "bad" },
    };
    expect(errorText(err, "fallback", "de")).toBe("Raum bad nicht gefunden.");
  });

  test("the weekday placeholder is named in the UI language", () => {
    useBackendErrors(
      hassWith({
        "component.roommind.exceptions.schedule_last_block.message": "{day}: Ende 24:00.",
      }),
    );
    const err = {
      code: "invalid_schedule",
      translation_key: "schedule_last_block",
      translation_placeholders: { day: "monday" },
    };
    expect(errorText(err, "fallback", "de")).toBe("Montag: Ende 24:00.");
  });

  test("without a loaded translation the English message is shown", () => {
    useBackendErrors(hassWith({}));
    const err = {
      code: "invalid_schedule",
      message: "Monday: invalid block.",
      translation_key: "schedule_block_invalid",
    };
    expect(errorText(err, "fallback", "en")).toBe("Monday: invalid block.");
  });
});
