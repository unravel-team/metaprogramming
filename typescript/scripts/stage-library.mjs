import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const sourcePackage = JSON.parse(readFileSync(resolve("package.json"), "utf8"));
const distDirectory = resolve("dist");
const libraryPackage = {
  name: sourcePackage.name,
  version: sourcePackage.version,
  description: sourcePackage.description,
  type: "module",
  main: "./index.js",
  types: "./index.d.ts",
  exports: {
    ".": {
      types: "./index.d.ts",
      default: "./index.js",
    },
  },
};

mkdirSync(distDirectory, { recursive: true });
writeFileSync(
  resolve(distDirectory, "package.json"),
  `${JSON.stringify(libraryPackage, null, 2)}\n`,
);
copyFileSync(resolve("README.library.md"), resolve(distDirectory, "README.md"));
