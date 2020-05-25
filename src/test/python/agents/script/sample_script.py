import random
from time import sleep

from rlbot.agents.base_script import BaseScript


class SampleScript(BaseScript):
    def run(self):
        for i in range(10):
            packet = self.get_game_tick_packet()
            self.renderer.begin_rendering()
            self.renderer.draw_string_2d(random.randint(200, 300), random.randint(20, 300), 1, 1,
                                         str(packet.game_info.seconds_elapsed), self.renderer.yellow())
            self.renderer.end_rendering()
            sleep(5)


print("Sample script starting...")
script = SampleScript("myScript")
script.run()
