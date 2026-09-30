"""Ad-hoc sign every Mach-O file, then frameworks, then the app bundle."""
import pathlib
import subprocess
import sys

MACHO_MAGIC = {bytes.fromhex(m) for m in ('feedface', 'feedfacf', 'cefaedfe', 'cffaedfe', 'cafebabe', 'bebafeca')}


def is_macho(path):
    with open(path, 'rb') as f:
        return f.read(4) in MACHO_MAGIC


def sign(path):
    subprocess.check_call(['codesign', '--force', '--sign', '-', str(path)])


def sign_bundle(bundle):
    bundle = pathlib.Path(bundle).resolve()
    binaries = [p for p in bundle.rglob('*') if p.is_file() and not p.is_symlink() and is_macho(p)]
    main = bundle / 'Contents/MacOS' / bundle.stem
    # Sign the main executable last among files; its signature seals the bundle later.
    for binary in sorted(binaries, key=lambda p: (p == main, -len(p.parts))):
        sign(binary)
    print(f'Signed {len(binaries)} Mach-O files')
    for framework in sorted(bundle.rglob('*.framework'), key=lambda p: -len(p.parts)):
        if framework.is_dir() and not framework.is_symlink():
            sign(framework)
    sign(bundle)
    unsigned = []
    for binary in binaries:
        result = subprocess.run(['codesign', '--verify', '--strict', str(binary)], capture_output=True, text=True)
        if result.returncode:
            kind = subprocess.run(['file', '-b', str(binary)], capture_output=True, text=True).stdout.strip()
            unsigned.append(f'{binary.relative_to(bundle)}: {kind}: {result.stderr.strip()}')
    if unsigned:
        sys.exit('Signing failed for:\n' + '\n'.join(unsigned))


if __name__ == '__main__':
    sign_bundle(sys.argv[1])
