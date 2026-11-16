import { describe, expect, it } from "vitest";
import type { RoomConfig } from "../types";
import { visibleRooms } from "./dashboard";

const rooms = {
  bad: { area_id: "bad" },
  kueche: { area_id: "kueche" },
  keller: { area_id: "keller" },
} as unknown as Record<string, RoomConfig>;

describe("visibleRooms", () => {
  it("leaves out rooms hidden on the dashboard", () => {
    expect(Object.keys(visibleRooms(rooms, ["keller"]))).toEqual(["bad", "kueche"]);
  });

  it("keeps a hidden room that was opened on purpose", () => {
    expect(Object.keys(visibleRooms(rooms, ["keller"], "keller"))).toEqual([
      "bad",
      "kueche",
      "keller",
    ]);
  });

  it("keeps every room when none is hidden", () => {
    expect(Object.keys(visibleRooms(rooms, []))).toEqual(["bad", "kueche", "keller"]);
  });
});
