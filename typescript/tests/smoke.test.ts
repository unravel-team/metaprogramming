import { describe, expect, it } from "vitest";
import { example } from "../src/index";

describe("example", () => {
  it.each([[0, 0], [2, 4], [-3, -6]])("doubles %i", (value, expected) => {
    expect(example(value)).toBe(expected);
  });
});
