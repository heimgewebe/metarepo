#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { execFileSync } from "child_process";
import { readFileSync, writeFileSync } from "fs";
import path from "path";

const splitArgs = (args) => args.split(/\s+/).filter(Boolean);

const server = new McpServer({
  name: "heimgewebe-local",
  version: "0.1.0"
});

// git
server.tool(
  "git",
  { args: z.string() },
  async ({ args }) => {
    const out = execFileSync("git", splitArgs(args), { encoding: "utf8" });
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
