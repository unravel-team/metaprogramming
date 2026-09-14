import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    exclude: [
      "**/*.property.test.ts",
      "**/*.integration.test.ts",
      "**/*.llm.test.ts",
      "node_modules/**",
    ],
    include: ["tests/**/*.test.ts"],
  },
});
