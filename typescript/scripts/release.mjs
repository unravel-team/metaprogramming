import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const packagePath = resolve("package.json");
const command = process.argv[2];
const packageJson = JSON.parse(readFileSync(packagePath, "utf8"));
const match = /^(\d+)\.(\d+)\.(\d+)$/.exec(packageJson.version);

if (!match) {
  throw new Error("package.json version must be a plain semantic version.");
}

const version = match.slice(1).map(Number);

if (command === "version") {
  console.log(packageJson.version);
  process.exit(0);
}

if (!new Set(["major", "minor", "patch"]).has(command)) {
  throw new Error("Usage: release.mjs version|major|minor|patch");
}

if (command === "major") {
  version[0] += 1;
  version[1] = 0;
  version[2] = 0;
} else if (command === "minor") {
  version[1] += 1;
  version[2] = 0;
} else {
  version[2] += 1;
}

packageJson.version = version.join(".");
writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`);
console.log(packageJson.version);
