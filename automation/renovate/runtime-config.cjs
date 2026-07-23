const path = require("node:path");

const here = __dirname;
const preset = require(path.join(here, "default.json"));
const scope = require(path.join(here, "expected-scope.v1.json"));

if (scope.runtime_mode !== "self-hosted-heim-pc") {
  throw new Error(`unexpected Renovate runtime_mode: ${scope.runtime_mode}`);
}
if (!Array.isArray(scope.expected_renovate_repositories) || scope.expected_renovate_repositories.length === 0) {
  throw new Error("expected_renovate_repositories must be a non-empty array");
}

module.exports = {
  ...preset,
  platform: "github",
  endpoint: "https://api.github.com/",
  repositories: scope.expected_renovate_repositories,
  autodiscover: false,
  onboarding: false,
  requireConfig: "optional",
  forkProcessing: "disabled",
  platformCommit: "enabled",
};
