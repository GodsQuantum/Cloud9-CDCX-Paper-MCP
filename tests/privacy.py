#!/usr/bin/env python3
"""Public tracked-file privacy audit: rejects personal infrastructure and credentials."""
from pathlib import Path
import re, subprocess, json, xml.etree.ElementTree as ET
base=Path(__file__).resolve().parent.parent
names=subprocess.check_output(['git','-C',str(base),'ls-files','-z']).decode().split(chr(0))
sensitive=[re.compile(q,re.I) for q in [
  'a'+'rezki','chou'+'gar','kech'+'idi','fe'+'lla',
  '/srv/'+'lxc/','/home/'+'arezki',r'192[.]168[.]',
  r'home[.]arpa',r'@gmail[.]com',r'-----BEGIN PRIVATE KEY',
  r'ghp_[a-zA-Z0-9]{25,}',r'github_pat_[A-Za-z0-9_]{25,}'
]]
bad=[]
for name in names:
  if not name or name=='tests/privacy.py':continue
  f=base/name
  if not f.is_file() or f.stat().st_size>500000:continue
  content=f.read_text(errors='replace')
  if any(x.search(content) for x in sensitive):bad.append(name)
assert not bad, "PRIVATE_INFO_PUBLICATION_BLOCKED "+str(sorted(set(bad)))
ET.parse(base/'docs/logo.svg');ET.parse(base/'docs/tools.svg')
contract=json.loads((base/'tests/contract-tools.json').read_text())
assert set(contract)=={'paper_balance','paper_positions','paper_history','paper_buy','paper_sell'}
print('CDCX_PUBLIC_SOURCE_AND_FIVE_TOOLS_CONTRACT_PRIVACY_PASS')
