#!/usr/bin/env python3
"""Install the official Crypto.com cdcx release asset after SHA256 validation."""
import hashlib
import io
import os
import pathlib
import re
import sys
import tarfile
import urllib.request

version, arch, destination = sys.argv[1:]
if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
    raise SystemExit("Invalid official release version")
if arch not in ("amd64", "arm64"):
    raise SystemExit("Unsupported architecture")
target = ("x86_64" if arch == "amd64" else "aarch64") + "-unknown-linux-musl"
asset = f"cdcx-{version}-{target}.tar.gz"
base = f"https://github.com/crypto-com/cdcx-cli/releases/download/v{version}/{asset}"
def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Cloud9-CdcxPaper-MCP-Builder"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()
tarball = get(base)
expected = get(base + ".sha256").decode("ascii").split()[0].lower()
actual = hashlib.sha256(tarball).hexdigest()
if not re.fullmatch("[a-f0-9]{64}", expected) or actual != expected:
    raise SystemExit("Official release asset checksum mismatch")
with tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz") as archive:
    members = [item for item in archive.getmembers()
               if item.isfile() and pathlib.PurePosixPath(item.name).name == "cdcx"]
    if len(members) != 1:
        raise SystemExit("Unexpected official archive layout")
    binary = archive.extractfile(members[0]).read()
if not binary.startswith(b"\x7fELF"):
    raise SystemExit("Official cdcx executable is not an ELF binary")
output = pathlib.Path(destination)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(binary)
os.chmod(output, 0o755)
print(f"OFFICIAL_CDCX_SHA256_VERIFIED={version} {arch} {actual[:12]}")
