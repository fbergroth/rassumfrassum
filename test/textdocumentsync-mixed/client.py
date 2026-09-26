#!/usr/bin/env python
"""
Test mixed text sync kinds (#55): primary incremental, secondary full.

rass must advertise Incremental to the client, translate to Full for
the full-sync server, and turn range-less resync changes into ranged
changes for incremental servers.  The servers assert their own
expectations (shape of didChange changes, final text via didSave).
"""

import asyncio

from rassumfrassum.test2 import LspTestEndpoint, log

URI = 'file:///tmp/test.md'
OPEN = 'line0\nline1\nline2\n'
MID = 'line0\nline1X\nline2!\n'
RESYNC = 'totally\ndifferent\n'


async def main():
    client = await LspTestEndpoint.create()
    init_response = await client.initialize()

    caps = init_response['result']['capabilities']
    sync = caps.get('textDocumentSync')
    log("client", f"Advertised textDocumentSync={sync}")
    assert isinstance(sync, dict) and sync.get('change') == 2, (
        f"Expected Incremental (change=2), got: {sync}"
    )

    await client.notify(
        'textDocument/didOpen',
        {
            'textDocument': {
                'uri': URI,
                'languageId': 'markdown',
                'version': 1,
                'text': OPEN,
            }
        },
    )

    # Two forward-sequential ranged changes (as an incremental client
    # would send)
    await client.notify(
        'textDocument/didChange',
        {
            'textDocument': {'uri': URI, 'version': 2},
            'contentChanges': [
                {
                    'range': {
                        'start': {'line': 1, 'character': 0},
                        'end': {'line': 1, 'character': 5},
                    },
                    'text': 'line1X',
                },
                {
                    'range': {
                        'start': {'line': 2, 'character': 5},
                        'end': {'line': 2, 'character': 5},
                    },
                    'text': '!',
                },
            ],
        },
    )
    await client.notify(
        'textDocument/didSave',
        {
            'textDocument': {'uri': URI},
            'text': MID,
        },
    )

    # Range-less "resync" change: rass must diff it into ranged
    # changes for the incremental server
    await client.notify(
        'textDocument/didChange',
        {
            'textDocument': {'uri': URI, 'version': 3},
            'contentChanges': [{'text': RESYNC}],
        },
    )
    await client.notify(
        'textDocument/didSave',
        {
            'textDocument': {'uri': URI},
            'text': RESYNC,
        },
    )

    log("client", "all didChange/didSave sequences sent")
    await client.byebye()


if __name__ == '__main__':
    asyncio.run(main())
