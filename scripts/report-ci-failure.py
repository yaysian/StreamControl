"""Emit GitHub error annotations for a failed build's log tail and failed tests."""
import pathlib
import sys
import xml.etree.ElementTree as ET


def annotate(title, text):
    text = text.replace('%', '%25').replace('\r', '').replace('\n', '%0A')
    print(f'::error title={title}::{text}')


def report(log, results):
    log, results = pathlib.Path(log), pathlib.Path(results)
    if log.is_file():
        lines = log.read_text(errors='replace').splitlines()
        annotate('Build log tail', '\n'.join(lines[-60:]))
    if results.is_file():
        for case in ET.parse(results).iter('testcase'):
            for bad in list(case.iter('failure')) + list(case.iter('error')):
                message = f"{bad.get('message', '')}\n{bad.text or ''}".strip()
                annotate(f"Test {case.get('name', '?')}", message)


if __name__ == '__main__':
    report(*sys.argv[1:])
