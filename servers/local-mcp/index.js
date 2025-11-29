#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { execSync } from "child_process";
import { readFileSync, writeFileSync } from "fs";

const server = new McpServer({
  name: "heimgewebe-local",
  version: "1.0.0"
});

server.tool(
  "git",
  { args: z.string() },
  async ({ args }) => {
    const out = execSync(`git ${args}`, { encoding: "utf8" });
    return { content: [{ type: "text", text: out }] };
  }
);

server.tool(
  "wgx",
  { args: z.string() },
  async ({ args }) => {
    const out = execSync(`wgx ${args}`, { encoding: "utf8" });
    return { content: [{ type: "text", text: out }] };
  }
);

server.tool(
  "fs_read",
  { path: z.string() },
  async ({ path }) => {
    const content = readFileSync(path, "utf8");
    return { content: [{ type: "text", text: content }] };
  }
);

server.tool(
  "fs_write",
  { path: z.string(), content: z.string() },
  async ({ path, content }) => {
    writeFileSync(path, content);
    return { content: [{ type: "text", text: "ok" }] };
  }
);

server.tool(
  "wgx_guard",
  { args: z.string().optional() },
  async ({ args }) => {
    const cmdArgs = args || "";
    const out = execSync(`./wgx guard ${cmdArgs}`, {
        encoding: "utf8",
        stdio: ["pipe", "pipe", "pipe"]
    });
    return { content: [{ type: "text", text: out }] };
  }
);

server.tool(
  "wgx_smoke",
  { args: z.string().optional() },
  async ({ args }) => {
    const cmdArgs = args || "";
    const out = execSync(`./wgx smoke ${cmdArgs}`, {
        encoding: "utf8",
        stdio: ["pipe", "pipe", "pipe"]
    });
    return { content: [{ type: "text", text: out }] };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
