#!/usr/bin/env python
"""Server with pull diagnostics."""
import argparse

from rassumfrassum.test2 import run_toy_server

parser = argparse.ArgumentParser()
parser.add_argument('--name', required=True)
args = parser.parse_args()

run_toy_server(
    name=args.name,
    capabilities={
        'diagnosticProvider': {
            'interFileDependencies': True,
            'workspaceDiagnostics': False,
        },
    },
    request_handlers={
        'textDocument/diagnostic': lambda msg_id, params: {
            'kind': 'full',
            'items': [],
        },
    },
)
