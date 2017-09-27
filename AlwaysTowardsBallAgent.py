import math

'''
This is v2 code
'''

'''
Hi! You can use this code as a template to create your own bot.  Also if you don't mind writing a blurb
about your bot's strategy you can put it as a comment here. I'd appreciate it, especially if I can help
debug any runtime issues that occur with your bot.
'''

# Optional Information. Fill out only if you wish.

# Your real name:
# Contact Email:
# Can this bot's code be shared publicly (Default: No):
# Can non-tournment gameplay of this bot be displayed publicly (Default: No):


# This is the name that will be displayed on screen in the real time display!
BOT_NAME = "AlwaysTowardsBallAgent"


class agent:

	def __init__(self, team):
		self.team = team # use self.team to determine what team you are. I will set to "blue" or "orange"

	def get_output_vector(self, sharedValue):
	
		UCONST_Pi = 3.1415926
		URotation180 = float(32768)
		URotationToRadians = UCONST_Pi / URotation180 
	
		gameTickPacket = sharedValue.GameTickPacket
		
		team1Blue = (gameTickPacket.gamecars[0].Team == 0)
	
		if team1Blue:
			blueIndex = 0
			orngIndex = 1
		else:
			blueIndex = 1
			orngIndex = 0
		
		ball_y = gameTickPacket.gameball.Location.Y
		ball_x = gameTickPacket.gameball.Location.X
		bluePitch = float(gameTickPacket.gamecars[blueIndex].Rotation.Pitch)
		blueYaw = float(gameTickPacket.gamecars[blueIndex].Rotation.Yaw)
		orngPitch = float(gameTickPacket.gamecars[orngIndex].Rotation.Pitch)
		orngYaw = float(gameTickPacket.gamecars[orngIndex].Rotation.Yaw)
		
		turn = 16383

		if (self.team == "blue"):
			player_y = gameTickPacket.gamecars[blueIndex].Location.Y
			player_x = gameTickPacket.gamecars[blueIndex].Location.X
			player_rot1 = math.cos(bluePitch * URotationToRadians) * math.cos(blueYaw * URotationToRadians) # Rot 1
			player_rot4 = math.cos(bluePitch * URotationToRadians) * math.sin(blueYaw * URotationToRadians) # Rot 4
		else:
			player_y = gameTickPacket.gamecars[orngIndex].Location.Y
			player_x = gameTickPacket.gamecars[orngIndex].Location.X
			player_rot1 = math.cos(orngPitch * URotationToRadians) * math.cos(orngYaw * URotationToRadians) # Rot 1
			player_rot4 = math.cos(orngPitch * URotationToRadians) * math.sin(orngYaw * URotationToRadians) # Rot 4
		
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
			turn = 0
		else:
			turn = 32767
		
		return [turn, 16383, 32767, 0, 0, 0, 0]
	