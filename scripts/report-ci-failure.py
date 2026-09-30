"""Emit GitHub error annotations for a failed build's log and failed tests."""
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

# GitHub truncates annotation messages at roughly 4 KB.
LIMIT = 3800
INTERESTING = re.compile(r'error|^Bundled |^Signed |^Replaced external|^Removed rpath|fail|traceback|assert|undefined|not found|cannot|\*\*\*', re.I)
NOISE = re.compile(r'replacing existing signature|^\S*/(clang\+\+|moc|uic|rcc) ')


def annotate(title, text):
    text = text[-LIMIT:].replace('%', '%25').replace('\r', '').replace('\n', '%0A')
    print(f'::error title={title}::{text}')


def shorten(line, width=400):
    return line if len(line) <= width else line[:width] + ' ...'


def report(log, results):
    log, results = pathlib.Path(log), pathlib.Path(results)
    if log.is_file():
        lines = [l for l in log.read_text(errors='replace').splitlines() if not NOISE.search(l)]
        errors = [shorten(l) for l in lines if INTERESTING.search(l)]
        if errors:
            annotate('Build errors', '\n'.join(errors[:40]))
        annotate('Build log tail', '\n'.join(shorten(l, 200) for l in lines[-25:]))
    if results.is_file():
        for case in ET.parse(results).iter('testcase'):
            for bad in list(case.iter('failure')) + list(case.iter('error')):
                message = f"{bad.get('message', '')}\n{bad.text or ''}".strip()
                annotate(f"Test {case.get('name', '?')}", message)


if __name__ == '__main__':
    report(*sys.argv[1:])
