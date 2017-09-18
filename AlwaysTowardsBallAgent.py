import math
import numpy as np

'''
This is v1 code using the old input format! If you are new please look at v2
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
		
	def convert_new_input_to_old_input(self, sharedValue):
	
		UU_TO_GAMEVALUES = 50
		
		UCONST_Pi = 3.1415926
		URotation180 = float(32768)
		URotationToRadians = UCONST_Pi / URotation180 
	
		inputs = np.zeros(38)
		scoring = np.zeros(12)
	
		gameTickPacket = sharedValue.GameTickPacket
		
		numCars = gameTickPacket.numCars
		numBoosts = gameTickPacket.numBoosts
		
		team1Blue = (gameTickPacket.CarInfo[0].Team == 0)
		
		if team1Blue:
			blueIndex = 0
			orngIndex = 1
		else:
			blueIndex = 1
			orngIndex = 0
		
		# -------------------------------
		# First convert ball info
		# -------------------------------
		
		# Ball positions
		inputs[2] = gameTickPacket.gameBall.Location.Y / UU_TO_GAMEVALUES
		inputs[7] = gameTickPacket.gameBall.Location.X / UU_TO_GAMEVALUES
		inputs[17] = gameTickPacket.gameBall.Location.Z / UU_TO_GAMEVALUES
		
		# Ball velocities
		inputs[28] = gameTickPacket.gameBall.Velocity.X  / UU_TO_GAMEVALUES
		inputs[29] = gameTickPacket.gameBall.Velocity.Z  / UU_TO_GAMEVALUES
		inputs[30] = gameTickPacket.gameBall.Velocity.Y  / UU_TO_GAMEVALUES
		
		# -------------------------------
		# Now do all scoreboard values
		# -------------------------------
		scoring[0] = gameTickPacket.CarInfo[blueIndex].Score.Goals + gameTickPacket.CarInfo[1].Score.OwnGoals # Blue Scoreboard Score
		scoring[1] = gameTickPacket.CarInfo[orngIndex].Score.Goals + gameTickPacket.CarInfo[0].Score.OwnGoals # Orange Scoreboard Score
		scoring[2] = gameTickPacket.CarInfo[orngIndex].Score.Demolitions # Demos by orange
		scoring[3] = gameTickPacket.CarInfo[blueIndex].Score.Demolitions # Demos by blue
		scoring[4] = gameTickPacket.CarInfo[blueIndex].Score.Score # Blue points
		scoring[5] = gameTickPacket.CarInfo[orngIndex].Score.Score # Orange points
		scoring[6] = gameTickPacket.CarInfo[blueIndex].Score.Goals # Blue Goals
		scoring[7] = gameTickPacket.CarInfo[blueIndex].Score.Saves # Blue Saves
		scoring[8] = gameTickPacket.CarInfo[blueIndex].Score.Shots # Blue Shots
		scoring[9] = gameTickPacket.CarInfo[orngIndex].Score.Goals # Orange Goals
		scoring[10] = gameTickPacket.CarInfo[orngIndex].Score.Saves # Orange Saves
		scoring[11] = gameTickPacket.CarInfo[orngIndex].Score.Shots # Orange Shots
			
		# -------------------------------
		# Now do all car values
		# -------------------------------
		
		# Blue pos
		inputs[1] = gameTickPacket.CarInfo[blueIndex].Location.Y / UU_TO_GAMEVALUES
		inputs[5] = gameTickPacket.CarInfo[blueIndex].Location.X / UU_TO_GAMEVALUES
		inputs[4] = gameTickPacket.CarInfo[blueIndex].Location.Z / UU_TO_GAMEVALUES
		
		# Orange pos
		inputs[3] = gameTickPacket.CarInfo[orngIndex].Location.Y / UU_TO_GAMEVALUES
		inputs[18] = gameTickPacket.CarInfo[orngIndex].Location.X / UU_TO_GAMEVALUES
		inputs[17] = gameTickPacket.CarInfo[orngIndex].Location.Z / UU_TO_GAMEVALUES
		
		# Blue velocity
		inputs[28] = gameTickPacket.CarInfo[blueIndex].Velocity.X / UU_TO_GAMEVALUES
		inputs[29] = gameTickPacket.CarInfo[blueIndex].Velocity.Z / UU_TO_GAMEVALUES
		inputs[30] = gameTickPacket.CarInfo[blueIndex].Velocity.Y / UU_TO_GAMEVALUES
		
		# Orange velocity
		inputs[34] = gameTickPacket.CarInfo[orngIndex].Velocity.X / UU_TO_GAMEVALUES
		inputs[35] = gameTickPacket.CarInfo[orngIndex].Velocity.Z / UU_TO_GAMEVALUES
		inputs[36] = gameTickPacket.CarInfo[orngIndex].Velocity.Y / UU_TO_GAMEVALUES
		
		# Boost
		inputs[0] = gameTickPacket.CarInfo[blueIndex].Boost
		inputs[37] = gameTickPacket.CarInfo[orngIndex].Boost
		
		# Rotations
		bluePitch = float(gameTickPacket.CarInfo[blueIndex].Rotation.Pitch)
		blueYaw = float(gameTickPacket.CarInfo[blueIndex].Rotation.Yaw)
		blueRoll = float(gameTickPacket.CarInfo[blueIndex].Rotation.Roll)
		orngPitch = float(gameTickPacket.CarInfo[orngIndex].Rotation.Pitch)
		orngYaw = float(gameTickPacket.CarInfo[orngIndex].Rotation.Yaw)
		orngRoll = float(gameTickPacket.CarInfo[orngIndex].Rotation.Roll)
		
		# Blue rotations
		inputs[8] = math.cos(bluePitch * URotationToRadians) * math.cos(blueYaw * URotationToRadians) # Rot 1
		inputs[9] = math.sin(blueRoll * URotationToRadians) * math.sin(bluePitch * URotationToRadians) * math.cos(blueYaw * URotationToRadians) - math.cos(blueRoll * URotationToRadians) * math.sin(blueYaw * URotationToRadians) # Rot2
		inputs[10] = -1 * math.cos(blueRoll * URotationToRadians) * math.sin(bluePitch * URotationToRadians) * math.cos(blueYaw * URotationToRadians) + math.sin(blueRoll * URotationToRadians) * math.sin(blueYaw * URotationToRadians)  # Rot 3
		inputs[11] = math.cos(bluePitch * URotationToRadians) * math.sin(blueYaw * URotationToRadians) # Rot 4
		inputs[12] = math.sin(blueRoll * URotationToRadians) * math.sin(bluePitch * URotationToRadians) * math.sin(blueYaw * URotationToRadians) + math.cos(blueRoll * URotationToRadians) * math.cos(blueYaw * URotationToRadians) # Rot5
		inputs[13] = -1 * math.sin(blueRoll * URotationToRadians) * math.cos(bluePitch * URotationToRadians) # Rot 6
		inputs[14] = math.cos(bluePitch * URotationToRadians)# Rot 7
		inputs[15] = math.cos(blueYaw * URotationToRadians) * math.sin(blueRoll * URotationToRadians) - math.cos(blueRoll * URotationToRadians) * math.sin(bluePitch * URotationToRadians) * math.sin(blueYaw * URotationToRadians) # Rot 8
		inputs[16] = math.cos(blueRoll * URotationToRadians) * math.cos(bluePitch * URotationToRadians) # Rot 9
		
		# Orange rot
		inputs[19] = math.cos(orngPitch * URotationToRadians) * math.cos(orngYaw * URotationToRadians) # Rot 1
		inputs[20] = math.sin(orngRoll * URotationToRadians) * math.sin(orngPitch * URotationToRadians) * math.cos(orngYaw * URotationToRadians) - math.cos(orngRoll * URotationToRadians) * math.sin(orngYaw * URotationToRadians) # Rot2
		inputs[21] = -1 * math.cos(orngRoll * URotationToRadians) * math.sin(orngPitch * URotationToRadians) * math.cos(orngYaw * URotationToRadians) + math.sin(orngRoll * URotationToRadians) * math.sin(orngYaw * URotationToRadians)  # Rot 3
		inputs[22] = math.cos(orngPitch * URotationToRadians) * math.sin(orngYaw * URotationToRadians) # Rot 4
		inputs[23] = math.sin(orngRoll * URotationToRadians) * math.sin(orngPitch * URotationToRadians) * math.sin(orngYaw * URotationToRadians) + math.cos(orngRoll * URotationToRadians) * math.cos(orngYaw * URotationToRadians) # Rot5
		inputs[24] = -1 * math.sin(orngRoll * URotationToRadians) * math.cos(orngPitch * URotationToRadians) # Rot 6
		inputs[25] = math.cos(orngPitch * URotationToRadians)# Rot 7
		inputs[26] = math.cos(orngYaw * URotationToRadians) * math.sin(orngRoll * URotationToRadians) - math.cos(orngRoll * URotationToRadians) * math.sin(orngPitch * URotationToRadians) * math.sin(orngYaw * URotationToRadians) # Rot 8
		inputs[27] = math.cos(orngRoll * URotationToRadians) * math.cos(orngPitch * URotationToRadians) # Rot 9
		
		return(inputs,scoring)

	def get_output_vector(self, sharedValue):
	
		input = self.convert_new_input_to_old_input(sharedValue)
		
		ball_z = input[0][2]
		ball_x = input[0][7]
		turn = 16383

		if (self.team == "blue"):
			player_z = input[0][1]
			player_x = input[0][5]
			player_rot1 = input[0][8]
			player_rot4 = input[0][11]
		else:
			player_z = input[0][3]
			player_x = input[0][18]
			player_rot1 = input[0][19]
			player_rot4 = input[0][22]
		
		# Need to handle atan2(0,0) case, aka straight up or down, eventually
		player_front_direction_in_radians = math.atan2(player_rot1, player_rot4)
		relative_angle_to_ball_in_radians = math.atan2((ball_x - player_x), (ball_z - player_z))

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
	