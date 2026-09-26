import * as hegel from "@hegeldev/hegel";
import * as gs from "@hegeldev/hegel/generators";
import { expect, it } from "vitest";
import { example } from "../src/index";

it("doubling is addition", () => {
  hegel.test((tc) => {
    const value = tc.draw(
      gs.integers({ minValue: -2_147_483_648, maxValue: 2_147_483_647 }),
    );
    expect(example(value)).toBe(value + value);
  });
});
