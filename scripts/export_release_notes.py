"""Export the curated notes for one vx.y release."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
def release_notes(version):
    if not re.fullmatch(r'v\d+\.\d+', version):
        raise ValueError('Version must use vx.y format')
    content = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    match = re.search(r'^## ' + re.escape(version) + r'\s*\n(.*?)(?=^## |\Z)', content, re.M | re.S)
    if not match or not match[1].strip():
        raise ValueError('Missing release notes for ' + version)
    return match[1].strip() + '\n'

if __name__ == '__main__':
    Path(sys.argv[2]).write_text(release_notes(sys.argv[1]), encoding='utf-8')
