from contextlib import contextmanager, closing
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty  # TODO(python 3.7+): use SimpleQueue
from threading import Thread
from typing import Iterator, Dict, Any, Tuple, Set
from urllib.parse import ParseResult as URL
import asyncio
import json
import socket
import time
from logging import Logger

from websockets.server import WebSocketServerProtocol, WebSocketServer
from websockets.exceptions import ConnectionClosed
import websockets

from rlbot.utils.logging_utils import get_logger
from rlbot.matchcomms.shared import MatchcommsPaths, JSON


logger = get_logger('matchcomms')

@dataclass
class MatchcommsServerThread:
    root_url: URL  # How to connect to the server.
    _server: WebSocketServer
    _event_loop: asyncio.AbstractEventLoop
    _thread: Thread

    def close(self, timeout=1):
        self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        self._thread.join(1)
        assert not self._thread.is_alive()

@contextmanager
def keep_in_set(element: Any, s: set):
    """
    Ensures the element is in the set while the context is running
    and removed afterwards.
    """
    s.add(element)
    logger.debug(f'+ client {element.host}:{element.port} (total of {len(s)} clients)')
    try:
        yield
    finally:
        s.remove(element)
        logger.debug(f'- client {element.host}:{element.port} (total of {len(s)} clients)')

@dataclass
class MatchcommsServer:
    users: Set[WebSocketServerProtocol] = field(default_factory=set) # TODO

    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        assert path == MatchcommsPaths.BROADCAST  # TODO consider using other channels
        with keep_in_set(websocket, self.users):
            try:
                async for message in websocket:
                    logger.debug(f'broadcast: {message}')
                    others = [user for user in self.users if user != websocket]
                    if len(others):
                        await asyncio.wait([
                            asyncio.ensure_future(other.send(message))
                            for other in others
                        ])
            except ConnectionClosed:
                return


def find_free_port() -> int:
    # https://stackoverflow.com/a/45690594
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def launch_matchcomms_server() -> MatchcommsServerThread:
    """
    Launches a background process that handles match communications.
    """
    host = 'localhost'
    port = find_free_port()  # deliberately not using a fixed port to prevent hardcoding fragility.

    event_loop = asyncio.new_event_loop()
    matchcomms_server = MatchcommsServer()
    start_server = websockets.serve(matchcomms_server.handle_connection, host, port, loop=event_loop)
    server = event_loop.run_until_complete(start_server)
    thread = Thread(target=event_loop.run_forever, daemon=True)
    thread.start()
    return MatchcommsServerThread(
        root_url=URL(scheme='ws', netloc=f'{host}:{port}', path='', params='', query='', fragment=''),
        _server=server,
        _event_loop=event_loop,
        _thread=thread,
    )


def self_test():
    server = launch_matchcomms_server()
    from rlbot.matchcomms.client import MatchcommsClient
    com1 = MatchcommsClient(server.root_url)
    com2 = MatchcommsClient(server.root_url)
    com1.outgoing_broadcast.put_nowait({'hi': 'there'})
    try:
        print('<', com2.incoming_broadcast.get(timeout=.2))
    except Empty as e:
        print('Did not get stuff from the queue.')
    com1.close()
    com2.close()
    server.close()


if __name__ == '__main__':
    self_test()
