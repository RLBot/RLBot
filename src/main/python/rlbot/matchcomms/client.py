from contextlib import contextmanager, closing
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty  # TODO(python 3.7+): use SimpleQueue
from typing import Iterator, Dict, Any, Tuple, Set
import json
import multiprocessing as mp
import socket
from dataclasses import dataclass, field
import asyncio
from threading import Thread

import websockets
from websockets.client import WebSocketClientProtocol

from rlbot.utils.logging_utils import get_logger
from rlbot.matchcomms.shared import MatchcommsPaths, JSON


class MatchcommsClient:
    def __init__(self, uri: str):
        self.uri = uri
        self.incoming_broadcast = Queue()
        self.outgoing_broadcast = Queue()

        self.event_loop = asyncio.new_event_loop()
        self._io_task = self.event_loop.create_task(self._run_queue_io())
        # self._io_handle = self.event_loop.call_soon_threadsafe(self._io_task)
        thread = Thread(target=self.event_loop.run_forever, daemon=True)
        thread.start()

    async def _run_queue_io(self):
        async with websockets.connect(self.uri + MatchcommsPaths.BROADCAST) as websocket:
            print('client connected to server')
            done, pending = await asyncio.wait(
                [
                    read_into_queue(websocket, self.incoming_broadcast),
                    send_from_queue(websocket, self.outgoing_broadcast),
                ],
                return_when=asyncio.FIRST_COMPLETED
            )
            print('client lost connection to server')
            for d in done:
                print('matchcomms client done: ', d.result())
            for p in pending:
                p.cancel()
        print('matchcomms exiting')

    def close(self):
        self._io_task.cancel()


def client_main(event_loop):
    """
    blocks indefinitely,
    """


async def read_into_queue(websocket, incoming: Queue):
    print('listening for messages from the server')

    async for message in websocket:
        # TODO: debug why this is never reached
        print('client got a message')
        # TODO: try/catch on parse errors
        incoming.put(json.parse(message))


async def send_from_queue(websocket, outgoing: Queue):
    while True:
        obj = outgoing.get()
        print(f'sending {obj}')
        await websocket.send(json.dumps(obj))
        print('send'+json.dumps(obj))


if __name__ == '__main__':
    from rlbot.matchcomms.server import self_test
    self_test()
