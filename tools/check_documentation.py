#!/usr/bin/env python3
"""Check maintained local Markdown/HTML links and the documentation archive receipt.

Run from any directory. Optional --archive-checkout verifies a separately fetched
archive at the exact migration pin, including original bytes and file modes.
Upstream omissions are exact, reviewed exceptions; new broken links still fail.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXCEPTIONS = ROOT / 'docs/validation/documentation-upstream-link-exceptions.json'


class Attributes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value and key in ('href', 'src'):
                self.links.append(value)


def links(text):
    # Examples in code fences are not document navigation.
    text = re.sub(r'^```[^\n]*\n.*?^```[^\n]*$', '', text, flags=re.M | re.S)
    text = re.sub(r'^~~~[^\n]*\n.*?^~~~[^\n]*$', '', text, flags=re.M | re.S)
    values = re.findall(r'\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+["\'][^)]*)?\)', text)
    values += re.findall(r'^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)', text, flags=re.M)
    parser = Attributes()
    parser.feed(text)
    return [v.strip('<>') for v in values + parser.links]


def local_target(source, link, root=ROOT):
    u = urlsplit(link)
    if u.scheme or u.netloc or not u.path:
        return None
    target = root / unquote(u.path).lstrip('/') if u.path.startswith('/') else source.parent / unquote(u.path)
    return target.resolve()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-checkout', type=Path)
    args = parser.parse_args()
    tracked = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-co', '--exclude-standard', '-z']).decode().split('\0')
    paths = sorted({p for p in tracked if p and (ROOT / p).is_file()})
    missing = set()
    fragments = []
    count = 0
    for name in paths:
        if Path(name).suffix.lower() not in {'.md', '.html', '.htm'}:
            continue
        for link in links((ROOT / name).read_text()):
            target = local_target(ROOT / name, link)
            if target is not None:
                count += 1
                if target.is_file() and urlsplit(link).fragment and target.suffix.lower() == '.md':
                    fragments.append((name, link, target))
                if not target.exists():
                    missing.add((name, link))
    exceptions = json.loads(EXCEPTIONS.read_text()) if EXCEPTIONS.exists() else {'links': []}
    known = {(e['source'], e['target']) for e in exceptions['links']}
    errors = []
    for source, digest in exceptions.get('source_sha256', {}).items():
        if hashlib.sha256((ROOT / source).read_bytes()).hexdigest() != digest:
            errors.append(f'Upstream exception source changed; review inventory: {source}')
    for source, link, target in fragments:
        anchors = set()
        seen = {}
        text = target.read_text()
        for heading in re.findall(r'^#{1,6} +(.+?) *#*$', text, flags=re.M):
            slug = re.sub(r'[^\w -]', '', heading.lower()).replace(' ', '-')
            n = seen.get(slug, 0)
            seen[slug] = n + 1
            anchors.add(slug + (f'-{n}' if n else ''))
        anchors.update(re.findall(r'(?:id|name)=[\"\']([^\"\']+)', text))
        if unquote(urlsplit(link).fragment) not in anchors:
            errors.append(f'Broken heading link: {source} -> {link}')
    for source, target in sorted(missing - known):
        errors.append(f'Broken local link: {source} -> {target}')
    for source, target in sorted(known - missing):
        errors.append(f'Stale link exception: {source} -> {target}')
    # Exceptions must remain confined to the pinned vendored toolkit.
    for source, _ in known:
        if not source.startswith('client/launcher/toolkit/'):
            errors.append(f'Non-upstream link exception: {source}')
    receipt = json.loads((ROOT / 'docs/validation/documentation-migration-2026-10-31.json').read_text())
    for entry in receipt['archive_files']:
        name = entry['original_path']
        # All moved screenshots must stay retired; validation/notices stay exact.
        if name.startswith('docs/launcher/'):
            if (ROOT / name).exists():
                errors.append(f'Retired screenshot reappeared: {name}')
        elif name.startswith('docs/validation/') or name in {'LICENSE', 'NOTICE', 'assets/launcher-icons/UPSTREAM-LICENSE'}:
            if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != entry['sha256']:
                errors.append(f'Preserved context changed: {name}')
    if args.archive_checkout:
        archive = args.archive_checkout.resolve()
        head = subprocess.check_output(['git', '-C', str(archive), 'rev-parse', 'HEAD']).decode().strip()
        if head != receipt['archive_commit']:
            errors.append('Archive checkout is not at the recorded pin')
        if hashlib.sha256((archive / 'manifest.json').read_bytes()).hexdigest() != receipt['archive_manifest_sha256']:
            errors.append('Archive manifest checksum differs')
        for entry in receipt['archive_files']:
            p = archive / entry['destination']
            if (not p.is_file() or p.is_symlink() or p.stat().st_size != entry['bytes']
                    or hashlib.sha256(p.read_bytes()).hexdigest() != entry['sha256']
                    or bool(p.stat().st_mode & 0o111) != (entry['git_mode'] == '100755')):
                errors.append(f'Archive integrity mismatch: {entry["destination"]}')
        # Check relative navigation in the migrated guides and archive index.
        docs = [archive / 'documentation-2026-10-31.md']
        docs += [archive / e['destination'] for e in receipt['archive_files']
                 if e['original_path'].startswith('docs/') and e['original_path'].endswith('.md')]
        for p in docs:
            for link in links(p.read_text()):
                target = local_target(p, link, archive)
                if target is not None and not target.exists():
                    errors.append(f'Broken archive link: {p.relative_to(archive)} -> {link}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {count} local links; {len(known)} exact pinned-upstream omissions; '
          f'{len(receipt["archive_files"])} migration records'
          + ('; independently fetched archive bytes/modes/index verified' if args.archive_checkout else ''))


if __name__ == '__main__':
    main()
