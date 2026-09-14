import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    include: ["tests/**/*.llm.test.ts"],
    passWithNoTests: true,
  },
});
