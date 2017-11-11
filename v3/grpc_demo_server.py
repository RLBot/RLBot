from concurrent import futures
import time
import math
import grpc

from grpcsupport.protobuf import game_data_pb2
from grpcsupport.protobuf import game_data_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class AlwaysTowardsBallBot(game_data_pb2_grpc.BotServicer):

	def GetControllerState(self, request, context):
		try:
			if (request.player_index < len(request.players)):
				return self.calculate_controller_state(request)

		except Exception as e:
			print('Exception running bot: ' + str(e))
			pass

		return game_data_pb2.ControllerState() # Return neutral input because we failed.


	def calculate_controller_state(self, request):
		controller_state = game_data_pb2.ControllerState()

		player = request.players[request.player_index]

		ball_x = request.ball.location.x
		ball_y = request.ball.location.y

		player_y = player.location.y
		player_x = player.location.x

		player_nose_y = math.cos(player.rotation.pitch) * math.cos(player.rotation.yaw)
		player_nose_x = math.cos(player.rotation.pitch) * math.sin(player.rotation.yaw)

		# Need to handle atan2(0,0) case, aka straight up or down, eventually
		player_front_direction_in_radians = math.atan2(player_nose_y, player_nose_x)
		relative_angle_to_ball_in_radians = math.atan2((ball_x - player_x), (ball_y - player_y))

		if (not (abs(player_front_direction_in_radians - relative_angle_to_ball_in_radians) < math.pi)):
			# Add 2pi to negative values
			if (player_front_direction_in_radians < 0):
				player_front_direction_in_radians += 2 * math.pi
			if (relative_angle_to_ball_in_radians < 0):
				relative_angle_to_ball_in_radians += 2 * math.pi

		if (relative_angle_to_ball_in_radians > player_front_direction_in_radians):
			controller_state.steer = -1
		else:
			controller_state.steer = 1

		controller_state.throttle = 1

		return controller_state


def serve():
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	game_data_pb2_grpc.add_BotServicer_to_server(AlwaysTowardsBallBot(), server)
	server.add_insecure_port('[::]:34865')
	server.start()
	print('Protobuf server listening on port 34865!')
	try:
		while True:
			time.sleep(_ONE_DAY_IN_SECONDS)
	except KeyboardInterrupt:
		server.stop(0)

if __name__ == '__main__':
	serve()
