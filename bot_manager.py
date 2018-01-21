import bot_input_struct as bi
import ctypes
from ctypes import *
from datetime import datetime, timedelta
import game_data_struct as gd
import importlib
import mmap
import os
import rate_limiter
import sys
import imp
import traceback

OUTPUT_SHARED_MEMORY_TAG = 'Local\\RLBotOutput'
INPUT_SHARED_MEMORY_TAG = 'Local\\RLBotInput'
GAME_TICK_PACKET_REFRESHES_PER_SECOND = 120  # 2*60. https://en.wikipedia.org/wiki/Nyquist_rate
MAX_AGENT_CALL_PERIOD = timedelta(seconds=1.0/30)  # Minimum call rate when paused.
REFRESH_IN_PROGRESS = 1
REFRESH_NOT_IN_PROGRESS = 0
MAX_CARS = 10


class BotManager:

    def __init__(self, terminateEvent, callbackEvent, name, team, index, modulename):
        self.terminateEvent = terminateEvent
        self.callbackEvent = callbackEvent
        self.name = name
        self.team = team
        self.index = index
        self.module_name = modulename


    def run(self):
        # Set up shared memory map (offset makes it so bot only writes to its own input!) and map to buffer
        buff = mmap.mmap(-1, ctypes.sizeof(bi.GameInputPacket), INPUT_SHARED_MEMORY_TAG)
        bot_input = bi.GameInputPacket.from_buffer(buff)
        player_input = bot_input.sPlayerInput[self.index]
        player_input_lock = (ctypes.c_long).from_address(ctypes.addressof(player_input))

        # Set up shared memory for game data
        game_data_shared_memory = mmap.mmap(-1, ctypes.sizeof(gd.GameTickPacketWithLock), OUTPUT_SHARED_MEMORY_TAG)
        bot_output = gd.GameTickPacketWithLock.from_buffer(game_data_shared_memory)
        lock = ctypes.c_long(0)
        game_tick_packet = gd.GameTickPacket() # We want to do a deep copy for game inputs so people don't mess with em


        # Create Ratelimiter
        r = rate_limiter.RateLimiter(GAME_TICK_PACKET_REFRESHES_PER_SECOND)
        last_tick_game_time = None  # What the tick time of the last observed tick was
        last_call_real_time = datetime.now()  # When we last called the Agent

        # Find car with same name and assign index
        for i in range(MAX_CARS):
            if str(bot_output.gamecars[i].wName) == self.name:
                self.index = i
                continue

        # Get bot module
        agent_module = importlib.import_module(self.module_name)
        # Create bot from module
        agent = agent_module.Agent(self.name, self.team, self.index)
        last_module_modification_time = os.stat(agent_module.__file__).st_mtime


        # Run until main process tells to stop
        while not self.terminateEvent.is_set():
            before = datetime.now()
            # Read from game data shared memory
            game_data_shared_memory.seek(0)  # Move to beginning of shared memory
            ctypes.memmove(ctypes.addressof(lock), game_data_shared_memory.read(ctypes.sizeof(lock)), ctypes.sizeof(lock)) # dll uses InterlockedExchange so this read will return the correct value!

            if lock.value != REFRESH_IN_PROGRESS:
                game_data_shared_memory.seek(4, os.SEEK_CUR) # Move 4 bytes past error code
                ctypes.memmove(ctypes.addressof(game_tick_packet), game_data_shared_memory.read(ctypes.sizeof(gd.GameTickPacket)),ctypes.sizeof(gd.GameTickPacket))  # copy shared memory into struct

            # Run the Agent only if the gameInfo has updated.
            tick_game_time = game_tick_packet.gameInfo.TimeSeconds
            should_call_while_paused = datetime.now() - last_call_real_time >= MAX_AGENT_CALL_PERIOD
            if tick_game_time != last_tick_game_time or should_call_while_paused:
                last_tick_game_time = tick_game_time
                last_call_real_time = datetime.now()

                try:
                    # Reload the Agent if it has been modified.
                    new_module_modification_time = os.stat(agent_module.__file__).st_mtime
                    if new_module_modification_time != last_module_modification_time:
                        last_module_modification_time = new_module_modification_time
                        print('Reloading Agent: ' + agent_module.__file__)
                        imp.reload(agent_module)
                        old_agent = agent
                        agent = agent_module.Agent(self.name, self.team, self.index)
                        # Retire after the replacement initialized properly.
                        if hasattr(old_agent, 'retire'):
                            old_agent.retire()


                    # Call agent
                    controller_input = agent.get_output_vector(game_tick_packet)

                    if not controller_input:
                        raise Exception('Agent "{}" did not return a player_input tuple.'.format(agent_module.__file__))

                    # Write all player inputs
                    player_input.fThrottle = controller_input[0]
                    player_input.fSteer = controller_input[1]
                    player_input.fPitch = controller_input[2]
                    player_input.fYaw = controller_input[3]
                    player_input.fRoll = controller_input[4]
                    player_input.bJump = controller_input[5]
                    player_input.bBoost = controller_input[6]
                    player_input.bHandbrake = controller_input[7]

                except Exception as e:
                    traceback.print_exc()

                # Workaround for windows streams behaving weirdly when not in command prompt
                sys.stdout.flush()
                sys.stderr.flush()

            # Ratelimit here
            after = datetime.now()
            # print('Latency of ' + self.name + ': ' + str(after - before))
            r.acquire(after-before)

        if hasattr(agent, 'retire'):
            agent.retire()
        # If terminated, send callback
        self.callbackEvent.set()
