#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { execFileSync } from "child_process";
import { readFileSync, writeFileSync } from "fs";
import { devNull } from "os";
import path from "path";
import { parseArgsStringToArgv } from "string-argv";

const splitArgs = (args) => parseArgsStringToArgv(args);

const server = new McpServer({
  name: "heimgewebe-local",
  version: "0.1.0"
});

// git
server.tool(
  "git",
  { args: z.string() },
  async ({ args }) => {
    // Strip dangerous git-related env vars before spawning; spread the rest so
    // PATH, HOME and similar essentials remain available.
    const {
      GIT_TRACE, GIT_TRACE_PACKET, GIT_TRACE2, GIT_TRACE2_EVENT,
      GIT_SSH_COMMAND, GIT_SSH, GIT_EXEC_PATH, GIT_PROXY_COMMAND,
      GIT_ASKPASS, GIT_CONFIG_COUNT,
      ...safeEnv
    } = process.env;
    const gitEnv = {
      ...safeEnv,
      GIT_CONFIG_GLOBAL: devNull,
      GIT_CONFIG_SYSTEM: devNull,
      // Empty string disables the pager entirely on all platforms.
      GIT_PAGER: "",
      // Use a platform-guaranteed no-op for the editor.
      GIT_EDITOR: process.platform === "win32" ? "cmd.exe /c exit 0" : "true"
    };
    const out = execFileSync("git", splitArgs(args), {
      encoding: "utf8",
      env: gitEnv
    });
    return { output: out };
  }
);

// wgx
server.tool(
  "wgx",
  { args: z.string() },
  async ({ args }) => {
    const out = execFileSync("scripts/wgx", splitArgs(args), { encoding: "utf8" });
    return { output: out };
  }
);

// WGX Guard
server.tool(
  "wgx_guard",
  { args: z.string().optional() },
  async ({ args = "" }) => {
    const out = execFileSync("scripts/wgx", ["guard", ...splitArgs(args)], { encoding: "utf8" });
    return { output: out };
  }
);

// WGX Smoke
server.tool(
  "wgx_smoke",
  { args: z.string().optional() },
  async ({ args = "" }) => {
    const out = execFileSync("scripts/wgx", ["smoke", ...splitArgs(args)], { encoding: "utf8" });
    return { output: out };
  }
);

const validatePath = (requestedPath) => {
  const root = process.cwd();
  const absolute = path.resolve(root, requestedPath);

  // Check if it's the root or starts with the root followed by a directory separator
  // to avoid sibling directory bypass (e.g., /app vs /app-secrets)
  const isWithin = absolute === root || absolute.startsWith(root + path.sep);
  if (!isWithin) {
    throw new Error(`Access denied: ${requestedPath} is outside of ${root}`);
  }
  return absolute;
};

// fs read
server.tool(
  "fs_read",
  { path: z.string() },
  async ({ path: requestedPath }) => {
    const safePath = validatePath(requestedPath);
    return { content: readFileSync(safePath, "utf8") };
  }
);

// fs write
server.tool(
  "fs_write",
  {
    path: z.string(),
    content: z.string()
  },
  async ({ path: requestedPath, content }) => {
    const safePath = validatePath(requestedPath);
    writeFileSync(safePath, content);
    return { ok: true };
  }
);

await server.connect(new StdioServerTransport());
