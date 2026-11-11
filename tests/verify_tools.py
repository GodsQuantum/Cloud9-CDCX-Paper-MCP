#!/usr/bin/env python3
"""Require complete MCP tool contracts and real native paper simulator."""
import asyncio
import json
import httpx
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

EXPECTED = json.loads(Path("/contract/contract-tools.json").read_text())

def normalize(x, root=False):
    if isinstance(x, list):
        return [normalize(i) for i in x]
    if isinstance(x, dict):
        return {key: normalize(value) for key, value in x.items()
                if not (key == "required" and value == [])
                and not (root and key == "title")}
    return x

async def check():
    async with streamable_http_client("http://127.0.0.1:18767/mcp") as conn:
        reader, writer = conn[:2]
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            response = await session.list_tools()
            observed = {}
            for tool in response.tools:
                obj = tool.model_dump(by_alias=True)
                observed[tool.name] = obj.get("inputSchema", obj.get("input_schema"))
            assert len(EXPECTED) == len(observed) == 5, f"tool count expected 5 got {len(observed)}"
            assert set(EXPECTED) == set(observed), f"tool names changed {set(EXPECTED) ^ set(observed)}"
            changed = [name for name in EXPECTED
                       if normalize(EXPECTED[name], True) != normalize(observed[name], True)]
            assert not changed, f"JSON argument schema regression: {changed}"
            print("CDCX_PAPER_FIVE_MCP_TOOLS_AND_INPUT_SCHEMAS_PASS", flush=True)
            result = await session.call_tool("paper_balance")
            assert not result.isError, "native paper balance read failed"
            print("CDCX_PAPER_NATIVE_READ_SIMULATION_PASS", flush=True)
    req = {"jsonrpc": "2.0", "id": 8, "method": "initialize",
           "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                      "clientInfo": {"name": "security-canary", "version": "1"}}}
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    a = httpx.post("http://127.0.0.1:18767/mcp", json=req,
                   headers={**h, "Host": "paper-test:18767"}, timeout=6)
    b = httpx.post("http://127.0.0.1:18767/mcp", json=req,
                   headers={**h, "Host": "malicious.invalid:18767"}, timeout=6)
    assert (a.status_code, b.status_code) == (200, 421), (
        "Host allowlist security changed", a.status_code, b.status_code)
    print("PAPER_STRICT_HOST_ALLOWLIST_200_421_PASS", flush=True)

asyncio.run(check())
