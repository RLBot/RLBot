import math

class agent:

	def get_output_vector(self, input):
		player_z = input[0][1]
		player_x = input[0][5]
		ball_z = input[0][2]
		ball_x = input[0][7]
		player_rot1 = input[0][8]
		player_rot4 = input[0][11]
		turn = 0.0
		
		# Need to handle atan2(0,0) case, aka straight up or down, eventually
		player_front_direction_in_radians = math.atan2(player_rot1, player_rot4)
		relative_angle_to_ball_in_radians = math.atan2((ball_x - player_x), (ball_z - player_z))
		
		if (abs(player_front_direction_in_radians - relative_angle_to_ball_in_radians) < math.pi):
			if (relative_angle_to_ball_in_radians > player_front_direction_in_radians):
				turn = -1.1
			else:
				turn = 1.1
		else:
			# Add 2pi to negative values
			if (player_front_direction_in_radians < 0):
				player_front_direction_in_radians += 2 * math.pi
			if (relative_angle_to_ball_in_radians < 0):
				relative_angle_to_ball_in_radians += 2 * math.pi
				
			if (relative_angle_to_ball_in_radians > player_front_direction_in_radians):
				turn = -1.1
			else:
				turn = 1.1
		
		return [1.1, turn, -1.1, -1.1, -1.1]
	