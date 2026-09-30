"""Copy @rpath dylibs that macdeployqt missed (e.g. libwebp -> libsharpyuv) into the bundle."""
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


if __name__ == '__main__':
    bundle_missing(sys.argv[1], [pathlib.Path(p) for p in sys.argv[2:]])
