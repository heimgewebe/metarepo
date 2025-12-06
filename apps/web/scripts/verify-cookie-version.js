import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const expectedVersion = process.env.COOKIE_VERSION ?? "0.7.2";
const cookiePackagePath = path.resolve(
  __dirname,
  "..",
  "node_modules",
  "cookie",
  "package.json"
);

if (!existsSync(cookiePackagePath)) {
  const message = "cookie package not installed; skipping version check";
  if (process.env.CI === "true") {
    console.error(message);
    process.exit(1);
  }
  console.warn(message);
  process.exit(0);
}

const cookiePackage = JSON.parse(readFileSync(cookiePackagePath, "utf8"));
const actualVersion = cookiePackage.version;

if (actualVersion !== expectedVersion) {
  console.error(
    `Expected cookie@${expectedVersion} but found ${actualVersion ?? "unknown"}.`
  );
  process.exit(1);
}

console.log(`cookie version OK (${actualVersion})`);
