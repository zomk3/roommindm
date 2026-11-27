import { describe, expect, it, test } from "vitest";
import type { HassArea, HomeAssistant, RoomConfig } from "../types";
import {
  floorGroups,
  floorOrderWithMove,
  orderedFloorIds,
  visibleRooms,
  type AreaInfo,
} from "./dashboard";

const floor = (floor_id: string, level: number | null) => ({ floor_id, name: floor_id, level });

// Object order as HA's frontend builds it; the registry order comes separately from rooms/list.
const hass = {
  language: "en",
  floors: {
    basement: floor("basement", -1),
    ground: floor("ground", 0),
    attic: floor("attic", 2),
  },
} as unknown as HomeAssistant;

function info(area_id: string, floor_id: string | null): AreaInfo {
  return {
    area: { area_id, name: area_id, floor_id } as HassArea,
    config: null,
    climateEntityCount: 0,
    tempSensorCount: 0,
  };
}

const infos = [
  info("kitchen", "ground"),
  info("bed", "attic"),
  info("cellar", "basement"),
  info("garden", null),
];

const keys = (order?: { ha: string[]; own: string[] }) =>
  floorGroups(infos, hass, true, order).map((g) => g.key);

describe("floorGroups order (#541)", () => {
  test("follows Home Assistant's floor order, no floor last", () => {
    expect(keys({ ha: ["ground", "attic", "basement"], own: [] })).toEqual([
      "ground",
      "attic",
      "basement",
      null,
    ]);
  });

  test("an order set in RoomMind wins, floors it does not name follow in HA's order", () => {
    expect(keys({ ha: ["basement", "ground", "attic"], own: ["attic"] })).toEqual([
      "attic",
      "basement",
      "ground",
      null,
    ]);
  });

  test("without an order from the backend the floors keep hass.floors order", () => {
    expect(keys()).toEqual(["basement", "ground", "attic", null]);
  });

  test("ignores deleted floors and duplicates in the stored orders", () => {
    expect(
      orderedFloorIds(hass, { ha: ["gone", "attic", "attic"], own: ["ground", "gone", "ground"] }),
    ).toEqual(["ground", "attic", "basement"]);
  });

  test("no grouping without floors", () => {
    const noFloors = { language: "en", floors: {} } as unknown as HomeAssistant;
    expect(floorGroups(infos, noFloors, true).map((g) => g.key)).toEqual([""]);
  });
});

describe("floorOrderWithMove", () => {
  const order = { ha: ["ground", "attic", "basement"], own: [] };
  const groups = floorGroups(infos, hass, true, order);

  test("moves a floor up among the shown ones", () => {
    expect(floorOrderWithMove(groups, hass, order, "attic", -1)).toEqual([
      "attic",
      "ground",
      "basement",
    ]);
  });

  test("returns null at the edge", () => {
    expect(floorOrderWithMove(groups, hass, order, "ground", -1)).toBeNull();
    expect(floorOrderWithMove(groups, hass, order, "basement", 1)).toBeNull();
  });

  test("floors without rooms keep their slot", () => {
    const shown = floorGroups(
      [info("kitchen", "ground"), info("cellar", "basement")],
      hass,
      true,
      order,
    );
    expect(floorOrderWithMove(shown, hass, order, "basement", -1)).toEqual([
      "basement",
      "attic",
      "ground",
    ]);
  });
});

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
