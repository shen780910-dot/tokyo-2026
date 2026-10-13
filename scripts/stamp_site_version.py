"""Link the published header version to the exact GitHub deployment commit."""
import os
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
sha = os.environ['GITHUB_SHA']
repository = os.environ['GITHUB_REPOSITORY']
if not re.fullmatch(r'[0-9a-f]{40}', sha):
    raise ValueError('Invalid GitHub commit SHA')
html = path.read_text(encoding='utf-8')
pattern = r'(<a\b[^>]*data-site-version\s+href=")[^"]+("[^>]*>)[^<]+(</a>)'
html, count = re.subn(pattern, lambda m: m[1] + f'https://github.com/{repository}/commit/{sha}' + m[2] + 'v' + sha[:7] + m[3], html)
if count != 1:
    raise ValueError('Expected exactly one header version link')
path.write_text(html, encoding='utf-8')
print('Stamped website version v' + sha[:7])
