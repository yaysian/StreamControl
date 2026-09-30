"""Make a macdeployqt bundle self-contained.

Copies @rpath dylibs that macdeployqt missed (e.g. libwebp -> libsharpyuv),
replaces symlinks that leave the bundle with real files, and removes LC_RPATH
entries that point back into Homebrew.
"""
import pathlib
import shutil
import subprocess
import sys


def output(*args):
    return subprocess.check_output(args, text=True)


def macho_files(bundle):
    for path in bundle.rglob('*'):
        if path.is_file() and not path.is_symlink() and 'Mach-O' in output('file', '-b', str(path)):
            yield path


def bundle_missing(bundle, search_dirs):
    bundle = pathlib.Path(bundle).resolve()
    frameworks = bundle / 'Contents/Frameworks'
    changed = True
    while changed:
        changed = False
        for binary in list(macho_files(bundle)):
            for line in output('otool', '-L', str(binary)).splitlines()[1:]:
                dependency = line.strip().split(' (compatibility version', 1)[0]
                name = dependency[len('@rpath/'):] if dependency.startswith('@rpath/') else ''
                # Frameworks are handled by macdeployqt; only plain dylibs are missed.
                if not name or '/' in name or name == binary.name:
                    continue
                target = frameworks / name
                if not target.exists():
                    source = next((d / name for d in search_dirs if (d / name).exists()), None)
                    if source is None:
                        sys.exit(f'Cannot find {name} needed by {binary}')
                    shutil.copy2(source.resolve(), target)
                    target.chmod(0o644)
                    subprocess.check_call(['install_name_tool', '-id', f'@executable_path/../Frameworks/{name}', str(target)])
                    print(f'Bundled {name} from {source}')
                    changed = True
                subprocess.check_call(['install_name_tool', '-change', dependency,
                                       f'@executable_path/../Frameworks/{name}', str(binary)])


def internalize_symlinks(bundle):
    bundle = pathlib.Path(bundle).resolve()
    for link in [p for p in bundle.rglob('*') if p.is_symlink()]:
        target = link.resolve()
        if target.is_relative_to(bundle):
            continue
        if not target.is_file():
            sys.exit(f'{link} points outside the bundle to {target}')
        link.unlink()
        shutil.copy2(target, link)
        link.chmod(0o644)
        print(f'Replaced external symlink {link.relative_to(bundle)} -> {target}')


def strip_external_rpaths(bundle):
    for binary in macho_files(pathlib.Path(bundle).resolve()):
        commands = output('otool', '-l', str(binary)).splitlines()
        for index, line in enumerate(commands):
            if line.strip() == 'cmd LC_RPATH':
                path = commands[index + 2].strip().split('path ', 1)[1].split(' (offset', 1)[0]
                if not path.startswith(('@loader_path', '@executable_path')):
                    subprocess.check_call(['install_name_tool', '-delete_rpath', path, str(binary)])
                    print(f'Removed rpath {path} from {binary.name}')


if __name__ == '__main__':
    internalize_symlinks(sys.argv[1])
    bundle_missing(sys.argv[1], [pathlib.Path(p) for p in sys.argv[2:]])
    strip_external_rpaths(sys.argv[1])
