from __future__ import annotations
import inspect
import os
import re
import subprocess
from typing import Optional
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

def configured_hosts() -> list[str]:
    hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
    for host in os.environ.get("MCP_ALLOWED_HOSTS", "").split(","):
        host = host.strip()
        if not host:
            continue
        if not re.fullmatch(r"(?:[A-Za-z0-9][A-Za-z0-9._-]{0,125}|(?:[0-9]{1,3}\.){3}[0-9]{1,3}):[0-9]{1,5}", host):
            raise ValueError("Invalid MCP_ALLOWED_HOSTS entry")
        if not 1 <= int(host.rsplit(":", 1)[1]) <= 65535:
            raise ValueError("Invalid MCP_ALLOWED_HOSTS port")
        hosts.append(host)
    return hosts

mcp=FastMCP(
    "Crypto.com CDCX Paper",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=configured_hosts(),
        allowed_origins=[]
    ),
    instructions="Local Crypto.com paper-trading simulator only. NO live exchange credentials are available. Buy/sell tools mutate simulated state only."
)

def run(*args:str)->str:
    p=subprocess.run(["cdcx",*args],text=True,capture_output=True,timeout=60)
    out=(p.stdout or "")+("\n"+p.stderr if p.stderr else "")
    if p.returncode!=0: raise RuntimeError(out.strip() or f"cdcx exit {p.returncode}")
    return out.strip()

@mcp.tool()
def paper_balance()->str:
    """Read simulated cash balance and P&L."""
    return run("paper","balance")

@mcp.tool()
def paper_positions()->str:
    """Read simulated open positions and unrealized/realized P&L."""
    return run("paper","positions")

@mcp.tool()
def paper_history()->str:
    """Read simulated trade history."""
    return run("paper","history")

@mcp.tool()
def paper_buy(instrument:str, quantity:float, limit_price:Optional[float]=None)->str:
    """SIMULATION ONLY: place a paper buy using live Crypto.com market prices or an optional limit price."""
    args=["paper","buy",instrument,"--quantity",str(quantity)]
    if limit_price is not None: args += ["--price",str(limit_price)]
    return run(*args)

@mcp.tool()
def paper_sell(instrument:str, quantity:float, limit_price:Optional[float]=None)->str:
    """SIMULATION ONLY: place a paper sell; never touches real funds."""
    args=["paper","sell",instrument,"--quantity",str(quantity)]
    if limit_price is not None: args += ["--price",str(limit_price)]
    return run(*args)

def serve():
    settings=getattr(mcp,"settings",None)
    if settings is not None:
        if hasattr(settings,"host"): settings.host="0.0.0.0"
        if hasattr(settings,"port"): settings.port=18767
        if hasattr(settings,"streamable_http_path"): settings.streamable_http_path="/mcp"
    params=inspect.signature(mcp.run).parameters
    if "host" in params or any(p.kind is p.VAR_KEYWORD for p in params.values()):
        mcp.run(transport="streamable-http",host="0.0.0.0",port=18767,streamable_http_path="/mcp")
    else: mcp.run(transport="streamable-http")

if __name__=="__main__": serve()
