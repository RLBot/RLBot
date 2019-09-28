import asyncio
import math
import webbrowser
import json
import os
import queue
import time
import shutil
from datetime import datetime, timedelta

import flatbuffers
import websockets
from rlbot.botmanager.agent_metadata import AgentMetadata
from rlbot.botmanager.bot_helper_process import BotHelperProcess
from rlbot.messages.flat import ControllerState, PlayerInput, TinyPacket, TinyPlayer, Vector3, Rotator, \
    TinyBall
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.game_interface import GameInterface
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

MAX_AGENT_CALL_PERIOD = timedelta(seconds=1.0)


def index_to_player_string(idx):
    return str(idx + 1)


class ScratchManager(BotHelperProcess):

    def __init__(self, agent_metadata_queue, quit_event, options):
        super().__init__(agent_metadata_queue, quit_event, options)
        self.logger = get_logger('scratch_mgr')
        self.game_interface = GameInterface(self.logger)
        self.current_sockets = set()
        self.running_indices = set()
        self.metadata_map = dict()
        self.port: int = options['port']
        self.sb3_file = options['sb3-file']
        self.pretend_blue_team = options['pretend_blue_team']
        self.has_received_input = False
        self.scratch_index_to_rlbot = {}
        self.should_flip_field = False

    async def data_exchange(self, websocket, path):
        async for message in websocket:
            try:
                controller_states = json.loads(message)
                if not self.has_received_input:
                    self.has_received_input = True
                    self.logger.info(f"Just got first input from Scratch {self.sb3_file} {self.port}")

                for key, scratch_state in controller_states.items():
                    scratch_index = int(key)
                    rlbot_index = self.get_rlbot_index(scratch_index)
                    self.game_interface.update_player_input_flat(self.convert_to_flatbuffer(scratch_state, rlbot_index))
            except UnicodeDecodeError:
                backup_location = os.path.join(os.path.dirname(self.sb3_file), f'backup-{str(int(os.path.getmtime(self.sb3_file)))}.sb3')
                print(f"Saving new version of {self.sb3_file} and backing up old version to {backup_location}")
                shutil.move(self.sb3_file, backup_location)
                with open(self.sb3_file, 'wb') as output:
                    output.write(message)

            self.current_sockets.add(websocket)

    def try_receive_agent_metadata(self):
        """
        As agents start up, they will dump their configuration into the metadata_queue.
        Read from it to learn about all the bots intending to use this scratch manager.
        """
        while True:  # will exit on queue.Empty
            try:
                single_agent_metadata: AgentMetadata = self.metadata_queue.get(timeout=0.1)
                self.running_indices.add(single_agent_metadata.index)
                self.metadata_map[single_agent_metadata.index] = single_agent_metadata
            except queue.Empty:
                return
            except Exception as ex:
                self.logger.error(ex)

    def start(self):
        self.logger.info("Starting scratch manager")

        self.game_interface.load_interface()

        # Wait a moment for all agents to have a chance to start up and send metadata
        time.sleep(1)
        self.try_receive_agent_metadata()

        self.logger.info(self.running_indices)

        num_scratch_bots = len(self.running_indices)
        if num_scratch_bots == 0:
            self.logger.error("No scratch bots registered in the scratch manager, exiting!")
            return

        self.setup_index_map()

        all_orange = sum(map(lambda meta: meta.team, self.metadata_map.values())) == len(self.running_indices)
        self.should_flip_field = self.pretend_blue_team and all_orange

        if self.options['spawn_browser']:
            options = Options()
            options.headless = self.options['headless']

            # This prevents an error message about AudioContext when running in headless mode.
            options.add_argument("--autoplay-policy=no-user-gesture-required")

            players_string = ",".join(map(index_to_player_string, range(len(self.running_indices))))

            try:
                driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
                driver.get(
                    f"http://scratch.rlbot.org?host=localhost:{str(self.port)}&players={players_string}&awaitBotFile=1")

                if self.sb3_file is not None:
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "sb3-selenium-uploader"))
                    )
                    element.send_keys(self.sb3_file)

            except SessionNotCreatedException:
                # This can happen if the downloaded chromedriver does not match the version of Chrome that is installed.
                webbrowser.open_new(
                    f"http://scratch.rlbot.org?host=localhost:{str(self.port)}&players={players_string}")
                self.logger.info(f"Could not load the Scratch file automatically! You'll need to upload it yourself "
                                 f"from {self.sb3_file}")

        asyncio.get_event_loop().run_until_complete(websockets.serve(self.data_exchange, port=self.port))
        asyncio.get_event_loop().run_until_complete(self.game_loop())

    def setup_index_map(self):
        num_scratch_bots = len(self.running_indices)
        sorted_indices = list(self.running_indices)
        sorted_indices.sort()
        self.scratch_index_to_rlbot = {i: r for i, r in enumerate(sorted_indices)}

        leftovers = [i for i in range(0, max(self.running_indices)) if i not in self.running_indices]
        leftovers.sort()
        for i in range(num_scratch_bots, num_scratch_bots + len(leftovers)):
            self.scratch_index_to_rlbot[i] = leftovers[i - num_scratch_bots]

    def get_rlbot_index(self, scratch_index):
        if scratch_index in self.scratch_index_to_rlbot:
            return self.scratch_index_to_rlbot[scratch_index]
        return scratch_index

    async def game_loop(self):

        last_tick_game_time = None  # What the tick time of the last observed tick was
        last_call_real_time = datetime.now()  # When we last called the Agent

        packet = GameTickPacket()

        # Run until main process tells to stop
        while not self.quit_event.is_set():
            before = datetime.now()

            self.game_interface.update_live_data_packet(packet)

            # Run the Agent only if the gameInfo has updated.
            tick_game_time = packet.game_info.seconds_elapsed
            worth_communicating = tick_game_time != last_tick_game_time or \
                                  datetime.now() - last_call_real_time >= MAX_AGENT_CALL_PERIOD

            ball = packet.game_ball
            if ball is not None and worth_communicating and max(self.running_indices) < packet.num_cars:
                last_tick_game_time = tick_game_time
                last_call_real_time = datetime.now()

                tiny_player_offsets = []
                builder = flatbuffers.Builder(0)

                for i in range(packet.num_cars):
                    tiny_player_offsets.append(self.copy_player(packet.game_cars[i], builder))

                TinyPacket.TinyPacketStartPlayersVector(builder, packet.num_cars)
                for i in reversed(range(0, len(tiny_player_offsets))):
                    rlbot_index = self.get_rlbot_index(i)
                    builder.PrependUOffsetTRelative(tiny_player_offsets[rlbot_index])
                players_offset = builder.EndVector(len(tiny_player_offsets))

                ballOffset = self.copy_ball(ball, builder)

                TinyPacket.TinyPacketStart(builder)
                TinyPacket.TinyPacketAddPlayers(builder, players_offset)
                TinyPacket.TinyPacketAddBall(builder, ballOffset)
                packet_offset = TinyPacket.TinyPacketEnd(builder)

                builder.Finish(packet_offset)
                buffer = bytes(builder.Output())

                filtered_sockets = {s for s in self.current_sockets if s.open}
                for socket in filtered_sockets:
                    await socket.send(buffer)

                self.current_sockets = filtered_sockets

            after = datetime.now()
            duration = (after - before).total_seconds()

            sleep_secs = 1 / 60 - duration
            if sleep_secs > 0:
                await asyncio.sleep(sleep_secs)

    def convert_to_flatbuffer(self, json_state: dict, index: int):
        builder = flatbuffers.Builder(0)

        ControllerState.ControllerStateStart(builder)
        ControllerState.ControllerStateAddSteer(builder, json_state['steer'])
        ControllerState.ControllerStateAddThrottle(builder, json_state['throttle'])
        ControllerState.ControllerStateAddPitch(builder, json_state['pitch'])
        ControllerState.ControllerStateAddYaw(builder, json_state['yaw'])
        ControllerState.ControllerStateAddRoll(builder, json_state['roll'])
        ControllerState.ControllerStateAddJump(builder, json_state['jump'])
        ControllerState.ControllerStateAddBoost(builder, json_state['boost'])
        ControllerState.ControllerStateAddHandbrake(builder, json_state['handbrake'])

        # This may throw a KeyError for anyone using old cached javascript. You should hard-refresh scratch.rlbot.org.
        ControllerState.ControllerStateAddUseItem(builder, json_state['useItem'])
        controller_state = ControllerState.ControllerStateEnd(builder)

        PlayerInput.PlayerInputStart(builder)
        PlayerInput.PlayerInputAddPlayerIndex(builder, index)
        PlayerInput.PlayerInputAddControllerState(builder, controller_state)
        player_input = PlayerInput.PlayerInputEnd(builder)

        builder.Finish(player_input)
        return builder

    def copy_v3(self, v3, builder):
        if self.should_flip_field:
            return Vector3.CreateVector3(builder, -v3.x, -v3.y, v3.z)
        return Vector3.CreateVector3(builder, v3.x, v3.y, v3.z)

    def copy_rot(self, rot, builder):
        yaw = rot.yaw
        if self.should_flip_field:
            yaw = yaw + math.pi if yaw < 0 else yaw - math.pi
        return Rotator.CreateRotator(builder, rot.pitch, yaw, rot.roll)

    def copy_player(self, player, builder):
        TinyPlayer.TinyPlayerStart(builder)
        TinyPlayer.TinyPlayerAddLocation(builder, self.copy_v3(player.physics.location, builder))
        TinyPlayer.TinyPlayerAddVelocity(builder, self.copy_v3(player.physics.velocity, builder))
        TinyPlayer.TinyPlayerAddRotation(builder, self.copy_rot(player.physics.rotation, builder))
        TinyPlayer.TinyPlayerAddTeam(builder, invert_team(player.team) if self.should_flip_field else player.team)
        TinyPlayer.TinyPlayerAddBoost(builder, player.boost)
        return TinyPlayer.TinyPlayerEnd(builder)

    def copy_ball(self, ball, builder):
        phys = ball.physics
        TinyBall.TinyBallStart(builder)
        TinyBall.TinyBallAddLocation(builder, self.copy_v3(phys.location, builder))
        TinyBall.TinyBallAddVelocity(builder, self.copy_v3(phys.velocity, builder))
        return TinyBall.TinyBallEnd(builder)


def invert_team(team):
    return 0 if team == 1 else 1
