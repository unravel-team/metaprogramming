import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    coverage: {
      all: true,
      include: ["src/index.ts", "src/app/**/*.ts"],
      provider: "v8",
      reporter: ["text", "lcov", "html"],
      reportsDirectory: "coverage",
    },
    environment: "node",
    exclude: [
      "**/*.integration.test.ts",
      "**/*.llm.test.ts",
      "node_modules/**",
    ],
    include: ["tests/**/*.test.ts"],
  },
});
