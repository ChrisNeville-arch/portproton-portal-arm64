#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Insert the two ARM64 compatibility branches without copying upstream scripts."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

WINE_ANCHOR = '    export MEDIACONV_BLANK_VIDEO_FILE='
RUNTIME_ANCHOR = 'pw_init_runtime () {'
WINE_BLOCK = '''    # Portal ARM64 compatibility
    if [[ "$(uname -m)" == "aarch64" && "$PW_WINE_USE" != "USE_SYSTEM_WINE" ]] ; then
        export WINE="$HOME/.local/bin/pp-wine"
        export WINELOADER="$WINE"
        export WINESERVER="$HOME/.local/bin/pp-wineserver"
        export PW_USE_RUNTIME=0
    fi

'''
RUNTIME_BLOCK = '''
    # Portal ARM64 native runtime
    if [[ "$(uname -m)" == "aarch64" ]] ; then
        export PW_USE_RUNTIME=0
        export PW_LD_LIBRARY_PATH=""
        export PW_VK_LAYER_PATH=""
        export PW_USE_INHIBIT_SLEEP=0
        export pw_runtime="env"
        return 0
    fi
'''


def transform(source):
    if source.count(WINE_ANCHOR) != 1 or source.count(RUNTIME_ANCHOR) != 1:
        raise ValueError('Unexpected upstream layout; inspect before patching.')
    wine_ok = WINE_BLOCK + WINE_ANCHOR in source
    runtime_ok = RUNTIME_ANCHOR + RUNTIME_BLOCK in source
    if wine_ok and runtime_ok:
        return source
    if 'Portal ARM64 compatibility' in source or 'Portal ARM64 native runtime' in source:
        raise ValueError('Partial or modified compatibility patch; inspect manually.')
    return source.replace(WINE_ANCHOR, WINE_BLOCK + WINE_ANCHOR, 1).replace(
        RUNTIME_ANCHOR, RUNTIME_ANCHOR + RUNTIME_BLOCK, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', nargs='?', type=Path,
                        default=Path.home() / 'PortProton/data/scripts/functions_helper')
    args = parser.parse_args()
    path = args.file.expanduser()
    if not path.is_file() or path.is_symlink():
        parser.exit(1, 'Expected a regular functions_helper file, not a symlink.\n')
    try:
        original = path.read_text(encoding='utf-8')
        patched = transform(original)
        if original == patched:
            print('Already patched; no changes made.')
            return
        backup = path.with_name(path.name + '.portal-arm64.original')
        if backup.exists() or backup.is_symlink():
            raise ValueError(f'Backup already exists: {backup}. Review it before reapplying.')
        fd, temp = tempfile.mkstemp(prefix='.portal-arm64-', dir=path.parent)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(patched)
            subprocess.run(['bash', '-n', temp], check=True)
            shutil.copymode(path, temp)
            shutil.copy2(path, backup)
            os.replace(temp, path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
        print(f'Patched {path}; backup: {backup}')
    except (OSError, ValueError, subprocess.CalledProcessError) as e:
        parser.exit(1, f'{e}\n')


if __name__ == '__main__':
    main()
