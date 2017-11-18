import bot_input_struct as bi
import ctypes
from ctypes import *
from datetime import datetime
import game_data_struct as gd
import importlib
import mmap
import rate_limiter
import sys

OUTPUT_SHARED_MEMORY_TAG = 'Local\\RLBotOutput'
INPUT_SHARED_MEMORY_TAG = 'Local\\RLBotInput'
RATE_LIMITED_ACTIONS_PER_SECOND = 60
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
        if sys.maxsize > 2**32:
            # 64 bit
            self.interlocked_exchange_dll = ctypes.CDLL('InterlockedWrapper', use_last_error=True)
            self.interlocked_exchange_fn = self.interlocked_exchange_dll.InterlockedExchangeWrapper
        else:
            # Assume 32 bit
            self.interlocked_exchange_dll = windll.kernel32
            self.interlocked_exchange_fn = self.interlocked_exchange_dll.InterlockedExchange



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

        # Get bot module
        agent_module = importlib.import_module(self.module_name)

        # Create Ratelimiter
        r = rate_limiter.RateLimiter(RATE_LIMITED_ACTIONS_PER_SECOND)

        # Find car with same name and assign index
        for i in range(MAX_CARS):
            if str(bot_output.gamecars[i].wName) == self.name:
                self.index = i
                continue

        # Create bot from module
        agent = agent_module.Agent(self.name, self.team, self.index)

        # Run until main process tells to stop
        while not self.terminateEvent.is_set():
            before = datetime.now()

            # Read from game data shared memory
            game_data_shared_memory.seek(0)  # Move to beginning of shared memory
            ctypes.memmove(ctypes.addressof(lock), game_data_shared_memory.read(ctypes.sizeof(lock)), ctypes.sizeof(lock)) # dll uses InterlockedExchange so this read will return the correct value!

            if lock.value != REFRESH_IN_PROGRESS:
                ctypes.memmove(ctypes.addressof(game_tick_packet), game_data_shared_memory.read(ctypes.sizeof(gd.GameTickPacket)),ctypes.sizeof(gd.GameTickPacket))  # copy shared memory into struct

            # Call agent
            controller_input = agent.get_output_vector(game_tick_packet)

            # Lock, Write, Unlock
            self.interlocked_exchange_fn(ctypes.byref(player_input_lock), ctypes.c_long(REFRESH_IN_PROGRESS))

            player_input.fThrottle = controller_input[0]
            player_input.fSteer = controller_input[1]
            player_input.fPitch = controller_input[2]
            player_input.fYaw = controller_input[3]
            player_input.fRoll = controller_input[4]
            player_input.bJump = controller_input[5]
            player_input.bBoost = controller_input[6]
            player_input.bHandbrake = controller_input[7]

            self.interlocked_exchange_fn(ctypes.byref(player_input_lock), ctypes.c_long(REFRESH_NOT_IN_PROGRESS))

            # Ratelimit here
            after = datetime.now()
            # print('Latency of ' + self.name + ': ' + str(after - before))

            r.acquire(after-before)

        # If terminated, send callback
        self.callbackEvent.set()



