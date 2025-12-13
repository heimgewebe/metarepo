#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { execSync } from "child_process";
import { readFileSync, writeFileSync } from "fs";

const server = new McpServer({
  name: "heimgewebe-local",
  version: "0.1.0"
});

// git
server.tool(
  "git",
  { args: z.string() },
  async ({ args }) => {
    const out = execSync(`git ${args}`, { encoding: "utf8" });
    return { output: out };
  }
);

// wgx
server.tool(
  "wgx",
  { args: z.string() },
  async ({ args }) => {
    const out = execSync(`scripts/wgx ${args}`, { encoding: "utf8" });
    return { output: out };
  }
);

// WGX Guard
server.tool(
  "wgx_guard",
  { args: z.string().optional() },
  async ({ args = "" }) => {
    const out = execSync(`scripts/wgx guard ${args}`, { encoding: "utf8" });
    return { output: out };
  }
);

// WGX Smoke
server.tool(
  "wgx_smoke",
  { args: z.string().optional() },
  async ({ args = "" }) => {
    const out = execSync(`scripts/wgx smoke ${args}`, { encoding: "utf8" });
    return { output: out };
  }
);

// fs read
server.tool(
  "fs_read",
  { path: z.string() },
  async ({ path }) => ({ content: readFileSync(path, "utf8") })
);

// fs write
server.tool(
  "fs_write",
  {
    path: z.string(),
    content: z.string()
  },
  async ({ path, content }) => {
    writeFileSync(path, content);
    return { ok: true };
  }
);

await server.connect(new StdioServerTransport());
