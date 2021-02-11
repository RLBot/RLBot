from threading import Thread

from rlbot.messages.flat.FieldInfo import FieldInfo
from rlbot.messages.flat.GameTickPacket import GameTickPacket
from rlbot.messages.flat.MatchSettings import MatchSettings
from rlbot.socket.socket_manager import SocketRelay


class SocketDataReporter:
    def __init__(self):
        self.latest_packet: GameTickPacket = None
        self.latest_field_info: FieldInfo = None
        self.latest_match_settings: MatchSettings = None

        self.socket_relay = SocketRelay()
        self.socket_relay.packet_handlers.append(self._handle_packet)
        self.socket_relay.field_info_handlers.append(self._handle_field_info)
        self.socket_relay.match_settings_handlers.append(self._handle_match_settings)

        self.thread = Thread(target=self.socket_relay.connect_and_run, args=(False, False, False))

        self.thread.start()

    def _handle_packet(self, packet: GameTickPacket):
        self.latest_packet = packet

    def _handle_field_info(self, field_info: FieldInfo):
        self.latest_field_info = field_info

    def _handle_match_settings(self, match_settings: MatchSettings):
        self.latest_match_settings = match_settings

    def disconnect(self):
        self.socket_relay.disconnect()


def get_one_packet() -> GameTickPacket:
    socket_relay = SocketRelay()
    packet = None
    def handle_packet(p):
        nonlocal packet
        packet = p
        socket_relay.disconnect()
    socket_relay.packet_handlers.append(handle_packet)
    socket_relay.connect_and_run(False, False, False)
    return packet
