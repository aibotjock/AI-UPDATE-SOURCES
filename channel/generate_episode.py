#!/usr/bin/env python3
"""Create a pending dated plan from the single active brief; perform no production."""
import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ZONE = ZoneInfo('America/New_York')


def generate(repo_root, output_root, episode, scope='opening', duration=None, now=None):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,39}', episode):
        raise ValueError('Episode ID must contain 1–40 letters, digits, hyphens or underscores.')
    if scope not in ('opening', 'full_episode'):
        raise ValueError('Scope must be opening or full_episode.')
    duration = duration if duration is not None else (60 if scope == 'opening' else 720)
    if duration <= 0:
        raise ValueError('Duration must be positive.')
    clock = now or datetime.now(ZONE)
    if clock.tzinfo is None:
        raise ValueError('Generation time must include a timezone.')
    clock = clock.astimezone(ZONE)
    canonical = Path(repo_root)/'channel/production-brief.txt'
    brief = canonical.read_bytes()
    folder = Path(output_root)/clock.date().isoformat()/episode
    folder.mkdir(parents=True)
    (folder/'production-brief-snapshot.txt').write_bytes(brief)
    status = {
        'schema_version': 2, 'episode': episode, 'scope': scope,
        'requested_duration_seconds': duration, 'generated_at': clock.isoformat(),
        'canonical_instruction': 'channel/production-brief.txt',
        'brief_sha256': hashlib.sha256(brief).hexdigest(),
        'stage': 'plan_only', 'research_completed': False,
        'model_tests_performed': False, 'narration_recorded': False,
        'powerpoint_playback_verified': False, 'video_rendered': False,
    }
    (folder/'episode-status.json').write_text(json.dumps(status,indent=2)+'\n',encoding='utf-8')
    (folder/'prompt.md').write_text(
        '# AI UPDATE — pending production request\n\n'
        f'Episode {episode}; scope {scope}; requested duration {duration} seconds.\n'
        f'Generated {clock.isoformat()}.\n\n'
        'Use channel/production-brief.txt as the only active production instructions. '
        'A byte-preserved snapshot is production-brief-snapshot.txt. '
        'Use reference and media catalogs as reference material, not additional rules. '
        'Later explicit user directions override the current request.\n\n'
        'This plan has not conducted research, run model tests, recorded narration, '
        'built media, or verified playback. Produce and verify the requested artifacts '
        'under the active brief before claiming completion.\n',encoding='utf-8')
    return folder


def validate(folder):
    folder = Path(folder)
    status = json.loads((folder/'episode-status.json').read_text(encoding='utf-8'))
    snapshot = (folder/'production-brief-snapshot.txt').read_bytes()
    if status.get('schema_version') != 2 or status.get('stage') != 'plan_only':
        raise ValueError('This checker only validates pending version-2 plan structure, not completed production.')
    if hashlib.sha256(snapshot).hexdigest() != status.get('brief_sha256'):
        raise ValueError('The retained brief snapshot does not match its hash.')
    if not (folder/'prompt.md').is_file():
        raise ValueError('Missing pending production request.')
    return 'Pending plan structure verified; no factual or playback verification asserted.'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command',required=True)
    create = commands.add_parser('generate')
    create.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1])
    create.add_argument('--output-root',type=Path)
    create.add_argument('--episode',required=True)
    create.add_argument('--scope',choices=['opening','full_episode'],default='opening')
    create.add_argument('--duration-seconds',type=int)
    check = commands.add_parser('validate')
    check.add_argument('folder',type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'generate':
            print(generate(args.repo_root,args.output_root or args.repo_root/'episodes',
                           args.episode,args.scope,args.duration_seconds))
        else:
            print(validate(args.folder))
    except (OSError,ValueError,TypeError,KeyError) as error:
        parser.exit(1,f'Error: {error}\n')


if __name__ == '__main__':
    main()
