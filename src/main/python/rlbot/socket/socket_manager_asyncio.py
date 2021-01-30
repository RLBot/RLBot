import asyncio
from asyncio import StreamReader, StreamWriter

from flatbuffers.builder import Builder
from rlbot.socket.socket_manager import SocketRelay, int_to_bytes, SocketDataType, SocketMessage, int_from_bytes


class SocketRelayAsyncio(SocketRelay):
    """
    A version of SocketRelay that uses asyncio. This is useful if you also want to run a websocket or something.

    Usage example:

    socket_relay = SocketRelayAsyncio()
    socket_relay.packet_handlers.append(self.whatever)

    relay_run = socket_relay.connect_and_run(wants_quick_chat=True, wants_game_messages=True,
                                                     wants_ball_predictions=True)
    websocket_server = websockets.serve(self.handle_connection, "localhost", 8765)
    asyncio.get_event_loop().run_until_complete(websocket_server)
    asyncio.get_event_loop().run_until_complete(relay_run)
    asyncio.get_event_loop().run_forever()
    """
    def __init__(self):
        super().__init__()
        self.writer: StreamWriter = None
        self.reader: StreamReader = None

    def send_flatbuffer(self, builder: Builder, data_type: SocketDataType):
        flatbuffer_bytes = builder.Output()
        size = len(flatbuffer_bytes)
        message = int_to_bytes(data_type) + int_to_bytes(size) + flatbuffer_bytes
        self.writer.write(message)

    async def read_from_socket_async(self) -> SocketMessage:
        type_int = int_from_bytes(await self.reader.readexactly(2))
        data_type = SocketDataType(type_int)
        size = int_from_bytes(await self.reader.readexactly(2))
        data = await self.reader.readexactly(size)
        return SocketMessage(data_type, data)

    async def wait_and_handle(self):
        incoming_message = await self.read_from_socket_async()
        self.handle_incoming_message(incoming_message)
        if self._should_continue:
            asyncio.create_task(self.wait_and_handle())
        else:
            await self.writer.drain()
            self.writer.close()

    async def connect_and_run(self, wants_quick_chat, wants_game_messages, wants_ball_predictions):
        """
        Connects to the socket and begins a loop that reads messages and calls any handlers
        that have been registered. Connect and run are combined into a single method because
        currently bad things happen if the buffer is allowed to fill up.
        """

        self.reader, self.writer, = await asyncio.open_connection('127.0.0.1', 23234)
        self.is_connected = True
        self.logger.info("Connected!")
        for handler in self.on_connect_handlers:
            handler()

        builder = self.make_ready_message(wants_ball_predictions, wants_game_messages, wants_quick_chat)
        self.send_flatbuffer(builder, SocketDataType.READY_MESSAGE)

        await self.wait_and_handle()
