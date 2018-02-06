####################################################################################################
# This RPC server responds to GetControllerState reqeusts by applying the
# "always steer for the ball" strategy. It also boosts because that's what the cool kids do.
#
# To run this agent successfully, you need to:
# - Install the python package "grpcio", e.g. pip install grpcio
# - Get RLBot to run the grpc_demo_agent.
# - Run this server at the same time as RLBot.
####################################################################################################

from concurrent import futures
import time
import math
import grpc

# Import the RPC protocol buffers. (needs a little bit of path hacking)
import os
import sys
from os.path import realpath, dirname
rlbot_directory = dirname(dirname(dirname(realpath(__file__))))
sys.path.append(rlbot_directory)
from grpcsupport.protobuf import game_data_pb2
from grpcsupport.protobuf import game_data_pb2_grpc


_ONE_DAY_IN_SECONDS = 60 * 60 * 24

def serve():
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	game_data_pb2_grpc.add_BotServicer_to_server(AlwaysTowardsBallBot(), server)
	server.add_insecure_port('[::]:34865')
	server.start()
	print('Grpc server listening on port 34865!')
	try:
		while True:
			time.sleep(_ONE_DAY_IN_SECONDS)
	except KeyboardInterrupt:
		server.stop(0)

class AlwaysTowardsBallBot(game_data_pb2_grpc.BotServicer):

	def GetControllerState(self, request, context):
		try:
			if request.player_index < len(request.players):
				return self.calculate_controller_state(request)

		except Exception as e:
			print('Exception running bot: ' + str(e))
			pass

		return game_data_pb2.ControllerState() # Return neutral input because we failed.


	def calculate_controller_state(self, request):

		ball_location = Vector2(request.ball.location.x, request.ball.location.y)

		my_car = request.players[request.player_index]
		car_location = Vector2(my_car.location.x, my_car.location.y)
		car_direction = get_car_facing_vector(my_car)
		car_to_ball = ball_location - car_location

		steer_correction_radians = car_direction.correction_to(car_to_ball)
		steer_magnitude = abs(steer_correction_radians)

		if steer_correction_radians > 0:
			# Positive radians in the unit circle is a turn to the left.
			turn = -1.0 # Negative value for a turn to the left.
		else:
			turn = 1.0

		controls = game_data_pb2.ControllerState()
		controls.throttle = 1
		controls.steer = turn if steer_magnitude > math.pi / 12 else turn * .2
		controls.boost = 1 if steer_magnitude < math.pi / 12 else 0
		controls.handbrake = 1 if steer_magnitude > math.pi / 2 else 0

		return controls


def get_car_facing_vector(car):

	pitch = float(car.rotation.pitch)
	yaw = float(car.rotation.yaw)

	facing_x = math.cos(pitch) * math.cos(yaw)
	facing_y = math.cos(pitch) * math.sin(yaw)

	return Vector2(facing_x, facing_y)


class Vector2:
	def __init__(self, x = 0, y = 0):
		self.x = float(x)
		self.y = float(y)

	def __add__(self, val):
		return Vector2( self.x + val.x, self.y + val.y)

	def __sub__(self,val):
		return Vector2( self.x - val.x, self.y - val.y)

	def __str__(self):
		return "(" + str(self.x) + ", " + str(self.y) + ")"

	def correction_to(self, ideal):
		current_in_radians = math.atan2(self.y, -self.x)
		ideal_in_radians = math.atan2(ideal.y, -ideal.x)

		correction = ideal_in_radians - current_in_radians

		# Make sure we go the 'short way'
		# The in-game axes are left handed, so use -x
		if not abs(correction) < math.pi:
			if correction < 0:
				correction += 2 * math.pi
			else:
				correction -= 2 * math.pi

		return correction


if __name__ == '__main__':
	serve()
