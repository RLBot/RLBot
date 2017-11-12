import math


class Agent:
    def __init__(self, name, team, index):
        self.name = name
        self.team = team  # 0 towards positive goal, 1 towards negative goal.
        self.index = index

    def get_output_vector(self, game_tick_packet):

        UCONST_Pi = 3.1415926
        URotation180 = float(32768)
        URotationToRadians = UCONST_Pi / URotation180

        gameTickPacket = game_tick_packet

        ball_y = gameTickPacket.gameball.Location.Y
        ball_x = gameTickPacket.gameball.Location.X
        pitch = float(gameTickPacket.gamecars[self.index].Rotation.Pitch)
        yaw = float(gameTickPacket.gamecars[self.index].Rotation.Yaw)

        turn = 0.0

        player_y = gameTickPacket.gamecars[self.index].Location.Y
        player_x = gameTickPacket.gamecars[self.index].Location.X
        # Nose vector x component
        player_rot1 = math.cos(pitch * URotationToRadians) * math.cos(yaw * URotationToRadians)
        # Nose vector y component
        player_rot4 = math.cos(pitch * URotationToRadians) * math.sin(yaw * URotationToRadians)

        # Need to handle atan2(0,0) case, aka straight up or down, eventually
        player_front_direction_in_radians = math.atan2(player_rot1, player_rot4)
        relative_angle_to_ball_in_radians = math.atan2((ball_x - player_x), (ball_y - player_y))

        if (not (abs(player_front_direction_in_radians - relative_angle_to_ball_in_radians) < math.pi)):
            # Add 2pi to negative values
            if (player_front_direction_in_radians < 0):
                player_front_direction_in_radians += 2 * math.pi
            if (relative_angle_to_ball_in_radians < 0):
                relative_angle_to_ball_in_radians += 2 * math.pi

        if (relative_angle_to_ball_in_radians > player_front_direction_in_radians):
            turn = -1.0
        else:
            turn = 1.0

        return [1.0, turn, 0.0, 0.0, 0.0, 0, 0, 0]

