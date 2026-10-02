#!/usr/bin/env python
"""Server with pull diagnostics: an error while an open document has "boom"."""
import argparse

from rassumfrassum.test2 import make_diagnostic, run_toy_server

parser = argparse.ArgumentParser()
parser.add_argument('--name', required=True)
parser.add_argument('--inter-file', action='store_true')
args = parser.parse_args()

docs = {}

def did_change(params):
    docs[params['textDocument']['uri']] = params['contentChanges'][-1]['text']

def diagnostic(msg_id, params):
    uri = params['textDocument']['uri']
    texts = docs.values() if args.inter_file else [docs.get(uri, '')]
    boom = any('boom' in t for t in texts)
    return {
        'kind': 'full',
        'items': [make_diagnostic(0, 0, 1, 1, 'boom')] if boom else [],
    }

run_toy_server(
    name=args.name,
    capabilities={
        'diagnosticProvider': {
            'interFileDependencies': args.inter_file,
            'workspaceDiagnostics': False,
        },
    },
    request_handlers={'textDocument/diagnostic': diagnostic},
    notification_handlers={'textDocument/didChange': did_change},
)
