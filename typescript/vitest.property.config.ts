import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    exclude: [
      "**/*.integration.property.test.ts",
      "**/*.llm.property.test.ts",
      "node_modules/**",
    ],
    include: ["tests/**/*.property.test.ts"],
  },
});
