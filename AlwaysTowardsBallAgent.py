import math

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

class agent:

	def __init__(self, team):
		self.team = team # use self.team to determine what team you are. I will set to "blue" or "orange"

	def get_bot_name(self):
		# This is the name that will be displayed on screen in the real time display!
		return "AlwaysTowardsBallAgent"

	def get_output_vector(self, input):
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
	