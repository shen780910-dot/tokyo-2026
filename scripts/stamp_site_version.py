"""Link the published header version to the exact GitHub deployment commit."""
import os
from pathlib import Path
import re
import sys
from export_release_notes import ROOT, release_notes

path = Path(sys.argv[1])
version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
notes = release_notes(version)
repository = os.environ.get('GITHUB_REPOSITORY', 'shen780910-dot/tokyo-2026')
html = path.read_text(encoding='utf-8')
pattern = r'(<a\b[^>]*data-site-version\s+href=")[^"]+("[^>]*>)[^<]+(</a>)'
html, count = re.subn(pattern, lambda m: m[1] + f'https://github.com/{repository}/releases' + m[2] + version + m[3], html)
if count != 1:
    raise ValueError('Expected exactly one header version link')
path.write_text(html, encoding='utf-8')
Path('release-notes.md').write_text(notes, encoding='utf-8')
print('Stamped website version ' + version)
