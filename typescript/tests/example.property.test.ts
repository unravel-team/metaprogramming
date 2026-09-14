import fc from "fast-check";
import { expect, it } from "vitest";
import { example } from "../src/index";

it("doubling is addition", () => {
  fc.assert(
    fc.property(fc.integer(), (value) => {
      expect(example(value)).toBe(value + value);
    }),
  );
});
