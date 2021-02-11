from typing import Dict

from rlbot.utils.structures.bot_input_struct import PlayerInput
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.hivemind.python_hivemind import PythonHivemind


# Link to Hivemind wiki: https://github.com/ViliamVadocz/Hivemind/wiki/

class HivemindTestHivemind(PythonHivemind):
    def initialize_hive(self, packet: GameTickPacket) -> None:
        self.logger.info(f"Initialised with {packet.num_cars} cars on pitch and {len(self.drone_indices)} on team!")

        # Find out team by looking at packet.
        # drone_indices is a set, so you cannot just pick first element.
        index = next(iter(self.drone_indices))
        self.team = packet.game_cars[index].team

        # Initialise objects and attributes here!
        # I suggest making a Car or Drone object for each of your drones
        # that will store info about them.

    def get_outputs(self, packet: GameTickPacket) -> Dict[int, PlayerInput]:

        # Your logic goes here!

        # Return a dictionary where the keys are indices of your drones and
        # the values are PlayerInput objects (the controller inputs).
        return {index: PlayerInput(throttle=1.0) for index in self.drone_indices}
