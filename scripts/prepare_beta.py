#!/usr/bin/env python3
"""Build a reviewable local beta; never publish, tag or access personal profiles."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
APP_ID = 'io.orbitz.YouTubeDesktop'

def run(*args):
    subprocess.run(list(map(str, args)), cwd=ROOT, check=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, default=Path('/tmp/orbitz-beta-build'))
    parser.add_argument('--repo', type=Path, default=Path('/tmp/orbitz-beta-repo'))
    parser.add_argument('--output', type=Path, default=ROOT/'dist')
    parser.add_argument('--check', action='store_true', help='Validate version metadata only')
    args=parser.parse_args()
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+-beta\.\d+',version):raise SystemExit('Invalid beta VERSION')
    releases=ET.parse(ROOT/'data/io.orbitz.YouTubeDesktop.metainfo.xml').find('releases')
    if releases[0].get('version')!=version or releases[0].get('type')!='development':raise SystemExit('AppStream version does not match VERSION')
    notes=ROOT/'docs/releases'/(version+'.md')
    if not notes.is_file():raise SystemExit('Missing release notes')
    if args.check:print('OK:',version);return
    if platform.machine()!='x86_64':raise SystemExit('Only x86_64 beta builds are supported')
    build=args.build_dir.resolve();repo=args.repo.resolve();output=args.output.resolve()
    # These locations are build inputs/outputs, never a user's installed app profile.
    if any(p in {ROOT,ROOT/'app',ROOT/'i18n',ROOT/'data',Path.home(),Path('/')} for p in (build,repo,output)):raise SystemExit('Unsafe build/output location')
    run('make','test')
    fresh=not (build/'metadata').is_file()
    if fresh:run('flatpak','build-init',build,APP_ID,'org.gnome.Sdk','org.gnome.Platform','49')
    run('make','install','PREFIX='+str(build/'files'))
    if fresh:
        permissions=json.loads((ROOT/'packaging/io.orbitz.YouTubeDesktop.json').read_text())['finish-args']
        run('flatpak','build-finish','--command=orbitz-youtube-wrapper',*permissions,build)
    run('flatpak','build-export',repo,build)
    output.mkdir(parents=True,exist_ok=True)
    bundle=output/('orbitz-youtube-api-player-'+version+'-x86_64.flatpak')
    run('flatpak','build-bundle',repo,bundle,APP_ID,'--runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo')
    shutil.copyfile(notes,output/'RELEASE_NOTES.md')
    paths=[ROOT/'VERSION',ROOT/'Makefile',ROOT/'data/io.orbitz.YouTubeDesktop.metainfo.xml']
    for folder in ('app','i18n','data/licenses'):
        paths += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo')]
    source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    (output/'BUILDINFO.json').write_text(json.dumps(dict(version=version,architecture='x86_64',runtime='org.gnome.Platform/49',source_hashes=source_hashes),indent=2)+'\n')
    artifacts=[bundle,output/'RELEASE_NOTES.md',output/'BUILDINFO.json']
    (output/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in artifacts))
    print('Prepared local beta:',bundle)

if __name__=='__main__':main()
