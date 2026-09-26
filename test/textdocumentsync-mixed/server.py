#!/usr/bin/env python
"""
Toy server with configurable textDocumentSync kind, tracking document
state.

Tracks the document it's told about, applying didChange content
changes to a mirror.  Full-sync servers assert that every didChange
carries a single range-less change; incremental servers assert that
every change has a range.  On didSave, asserts that the mirror matches
the expected text, so the client can check rass's translations.
"""

import argparse
import os
import sys

from rassumfrassum.test2 import run_toy_server

parser = argparse.ArgumentParser()
parser.add_argument('--name', required=True)
parser.add_argument(
    '--text-document-sync',
    type=int,
    default=2,
    help='textDocumentSync kind: 1=Full, 2=Incremental',
)
args = parser.parse_args()

sync_kind = args.text_document_sync
state = {'doc': ''}


def fail(msg):
    print(f"FAIL: {msg}", file=sys.stderr, flush=True)
    os._exit(1)


def offset(text, pos):
    """Offset of an LSP position (code points = UTF-16 units here)."""
    return (
        sum(len(l) + 1 for l in text.split('\n')[: pos['line']])
        + pos['character']
    )


def apply_changes(text, changes):
    """Apply didChange content changes in order (see LSP spec)."""
    for change in changes:
        new = change.get('text', '')
        if (r := change.get('range')) is None:
            text = new
        else:
            start = offset(text, r['start'])
            end = offset(text, r['end'])
            text = text[:start] + new + text[end:]
    return text


def did_open(params):
    state['doc'] = params['textDocument']['text']


def did_change(params):
    changes = params['contentChanges']
    if sync_kind == 1:
        if not (len(changes) == 1 and 'range' not in changes[0]):
            fail(f"full-sync server got ranged changes: {changes}")
    else:
        if not all('range' in c for c in changes):
            fail(f"incremental server got range-less change: {changes}")
    state['doc'] = apply_changes(state['doc'], changes)


def did_save(params):
    if state['doc'] != params.get('text'):
        fail(
            f"server {args.name} doc mismatch: {state['doc']!r} "
            f"vs expected {params.get('text')!r}"
        )


run_toy_server(
    name=args.name,
    capabilities={
        'textDocumentSync': {
            'change': sync_kind,
            'openClose': True,
            'save': True,
        },
        'hoverProvider': True,
    },
    notification_handlers={
        'textDocument/didOpen': did_open,
        'textDocument/didChange': did_change,
        'textDocument/didSave': did_save,
    },
)
