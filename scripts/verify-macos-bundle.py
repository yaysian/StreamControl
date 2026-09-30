"""Reject wrong-architecture binaries and dependencies outside the app/system."""
import pathlib
import subprocess
import sys


def output(*args):
    return subprocess.check_output(args, text=True)


def verify(bundle, architecture):
    bundle = pathlib.Path(bundle).resolve()
    executable_dir = bundle / 'Contents/MacOS'
    assert (executable_dir / 'StreamControl').is_file(), 'Missing executable'
    assert (bundle / 'Contents/PlugIns/platforms/libqcocoa.dylib').is_file(), 'Missing Cocoa plugin'
    binaries = 0
    for link in bundle.rglob('*'):
        if link.is_symlink():
            assert link.resolve().is_relative_to(bundle) and link.exists(), (link, link.resolve())
    for binary in bundle.rglob('*'):
        if binary.is_symlink() or not binary.is_file():
            continue
        if 'Mach-O' not in output('file', '-b', str(binary)):
            continue
        binaries += 1
        assert architecture in output('lipo', '-archs', str(binary)).split(), binary
        load_commands = output('otool', '-l', str(binary)).splitlines()
        rpaths = []
        for index, line in enumerate(load_commands):
            if line.strip() == 'cmd LC_RPATH':
                rpaths.append(load_commands[index + 2].strip().split('path ', 1)[1].split(' (offset', 1)[0])
        def expand(path):
            return pathlib.Path(path.replace('@loader_path', str(binary.parent)).replace('@executable_path', str(executable_dir))).resolve()
        def internal(path):
            return path.is_relative_to(bundle) and path.exists()
        for path in rpaths:
            assert path.startswith(('@loader_path', '@executable_path')) and expand(path).is_relative_to(bundle), (binary, path)
        # A dylib's own install name is listed by otool -L but is not a dependency.
        own_id = output('otool', '-D', str(binary)).splitlines()[1:]
        for line in output('otool', '-L', str(binary)).splitlines()[1:]:
            dependency = line.strip().split(' (compatibility version', 1)[0]
            if dependency in own_id:
                continue
            if dependency.startswith(('/System/Library/', '/usr/lib/')):
                continue
            if dependency.startswith('@rpath/'):
                suffix = dependency[len('@rpath/'):]
                candidates = [expand(path) / suffix for path in rpaths]
                # macdeployqt also uses an executable-level Frameworks search path.
                candidates.append(bundle / 'Contents/Frameworks' / suffix)
                assert any(internal(p.resolve()) for p in candidates), (binary, dependency)
            else:
                assert dependency.startswith(('@loader_path/', '@executable_path/')), (binary, dependency)
                assert internal(expand(dependency)), (binary, dependency)
    assert binaries, 'No Mach-O binaries found'
    print(f'Verified {binaries} Mach-O files for {architecture}')


if __name__ == '__main__':
    verify(*sys.argv[1:])
