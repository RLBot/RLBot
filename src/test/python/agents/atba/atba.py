import math
from random import random

from rlbot.agents.base_agent import BaseAgent, BOT_CONFIG_AGENT_HEADER, SimpleControllerState
from rlbot.messages.flat.RumbleOption import RumbleOption
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.game_state_util import GameState, BoostState, BallState, CarState, GameInfoState, Physics, Vector3
from rlbot.utils.game_state_util import Rotator
from rlbot.utils.structures.game_data_struct import GameTickPacket, DropshotTileState
from rlbot.utils.structures.quick_chats import QuickChats


class Atba(BaseAgent):
    flip_turning = False
    test_rendering = False
    test_quickchat = False
    test_dropshot = False
    test_state = False
    test_ball_prediction = False
    test_physics_tick = False
    cleared = False

    def get_output(self, game_tick_packet: GameTickPacket) -> SimpleControllerState:
        controller_state = SimpleControllerState()

        if not game_tick_packet.game_info.is_round_active:
            return controller_state

        ball_location = Vector2(game_tick_packet.game_ball.physics.location.x,
                                game_tick_packet.game_ball.physics.location.y)

        my_car = game_tick_packet.game_cars[self.index]
        car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        car_direction = get_car_facing_vector(my_car)
        car_to_ball = ball_location - car_location

        steer_correction_radians = car_direction.correction_to(car_to_ball)

        if steer_correction_radians > 0:
            # Positive radians in the unit circle is a turn to the left.
            turn = -1.0  # Negative value for a turn to the left.
        else:
            turn = 1.0

        if self.flip_turning:
            turn *= -1.0

        if self.test_quickchat:
            if turn == -1.0 and random() > .99:
                self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Information_IGotIt)

            if turn == 1.0 and random() > .99:
                self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Reactions_HolyCow)

        if self.test_rendering:
            self.do_rendering_test(game_tick_packet, my_car)

        if self.test_dropshot:
            self.do_dropshot_tile_test(game_tick_packet)

        if self.test_state:
            self.set_state_test(game_tick_packet)

        if self.test_ball_prediction:
            self.render_ball_prediction()

        if self.test_physics_tick:
            self.do_physics_tick_test(game_tick_packet)

        # Not making this configurable because it's easier to just modify the code
        # self.render_packet(game_tick_packet)

        if random() > .99:
            game_map = self.get_match_settings().MutatorSettings().RumbleOption()
            self.logger.info(f'Is Spike Rush? {game_map == RumbleOption.Spike_Rush}')

        controller_state.throttle = 1.0
        controller_state.steer = turn
        controller_state.use_item = random() > .99

        return controller_state

    def render_packet(self, game_tick_packet):
        self.renderer.begin_rendering()

        self.render_value(5, 100, 1, "seconds_elapsed", game_tick_packet.game_info.seconds_elapsed)
        self.render_value(5, 100, 2, "game_time_remaining", game_tick_packet.game_info.game_time_remaining)
        self.render_value(5, 100, 3, "is_overtime", game_tick_packet.game_info.is_overtime)
        self.render_value(5, 100, 4, "is_unlimited_time", game_tick_packet.game_info.is_unlimited_time)
        self.render_value(5, 100, 5, "is_round_active", game_tick_packet.game_info.is_round_active)
        self.render_value(5, 100, 6, "is_kickoff_pause", game_tick_packet.game_info.is_kickoff_pause)
        self.render_value(5, 100, 7, "is_match_ended", game_tick_packet.game_info.is_match_ended)
        self.render_value(5, 100, 8, "world_gravity_z", game_tick_packet.game_info.world_gravity_z)
        self.render_value(5, 100, 9, "game_speed", game_tick_packet.game_info.game_speed)

        self.render_value(5, 100, 11, "blue score", game_tick_packet.teams[0].score)
        self.render_value(5, 100, 12, "orange score", game_tick_packet.teams[1].score)

        self.render_value(5, 100, 14, "latest touch player", game_tick_packet.game_ball.latest_touch.player_name)
        self.render_value(5, 100, 15, "latest touch location", game_tick_packet.game_ball.latest_touch.hit_location)
        self.render_value(5, 100, 16, "latest touch normal", game_tick_packet.game_ball.latest_touch.hit_normal)
        self.render_value(5, 100, 17, "latest touch seconds", game_tick_packet.game_ball.latest_touch.time_seconds)
        self.render_value(5, 100, 18, "latest touch team", game_tick_packet.game_ball.latest_touch.team)

        for i in range(0, game_tick_packet.num_cars):
            self.render_player(game_tick_packet, i)

        self.renderer.end_rendering()

    def render_player(self, game_tick_packet, index):
        player = game_tick_packet.game_cars[index]
        self.render_value_3d(player.physics.location, 0, "is_demolished", player.is_demolished)
        self.render_value_3d(player.physics.location, 1, "has_wheel_contact", player.has_wheel_contact)
        self.render_value_3d(player.physics.location, 2, "is_super_sonic", player.is_super_sonic)
        self.render_value_3d(player.physics.location, 3, "is_bot", player.is_bot)
        self.render_value_3d(player.physics.location, 4, "jumped", player.jumped)
        self.render_value_3d(player.physics.location, 5, "double_jumped", player.double_jumped)
        self.render_value_3d(player.physics.location, 6, "team", player.team)
        self.render_value_3d(player.physics.location, 7, "boost", player.boost)

    def render_value_3d(self, vec, index, label, value):

        text = f"{label}: {value}"
        if type(value) is float:
            text = f"{label}: {value:.2f}"

        self.renderer.draw_string_3d((vec.x, vec.y, vec.z + 100 - index * 12), 1, 1, text, self.renderer.white())

    def render_value(self, x, y_basis, index, label, value):

        if type(value) is bool:
            if value:
                color = self.renderer.cyan()
            else:
                color = self.renderer.create_color(255, 255, 200, 200)
        else:
            color = self.renderer.white()

        text = f"{label}: {value}"
        if type(value) is float:
            text = f"{label}: {value:.2f}"

        self.renderer.draw_string_2d(x, y_basis + index * 20, 1, 1, text, color)

    def do_rendering_test(self, game_tick_packet, my_car):
        if self.cleared:
            self.renderer.clear_screen()
        else:
            car_render_location = [my_car.physics.location.x, my_car.physics.location.y, my_car.physics.location.z]
            ball_render_location = [game_tick_packet.game_ball.physics.location.x,
                                    game_tick_packet.game_ball.physics.location.y,
                                    game_tick_packet.game_ball.physics.location.z]
            text = 'touch x:' + str(game_tick_packet.game_ball.latest_touch.hit_location.x) + '\ntime: ' \
                   + str(game_tick_packet.game_ball.latest_touch.time_seconds)

            self.renderer.begin_rendering()
            color = self.renderer.create_color(121, 121, 0, 121)
            color2 = self.renderer.create_color(255, 0, 255, 255)
            self.renderer.draw_line_2d(100, 100, 1000, 500, self.renderer.black())
            self.renderer.draw_rect_2d(0, 0, 50, 50, True, color)
            self.renderer.draw_line_3d((50, 50, 50), car_render_location, color2)
            self.renderer.draw_line_2d_3d(100, 100, car_render_location, color2)
            self.renderer.draw_rect_3d(car_render_location, 100, 100, True, self.renderer.create_color(200, 0, 0, 0))
            self.renderer.draw_string_2d(100, 100, 2, 2, text, self.renderer.white())
            self.renderer.draw_string_3d(ball_render_location, 2, 2, "BALL", self.renderer.red())

            if game_tick_packet.game_info.is_kickoff_pause:
                # Color showcase
                self.renderer.draw_string_2d(10, 120, 1, 1, "black", self.renderer.black())
                self.renderer.draw_string_2d(10, 135, 1, 1, "white", self.renderer.white())
                self.renderer.draw_string_2d(10, 150, 1, 1, "gray", self.renderer.gray())
                self.renderer.draw_string_2d(10, 165, 1, 1, "red", self.renderer.red())
                self.renderer.draw_string_2d(10, 180, 1, 1, "orange", self.renderer.orange())
                self.renderer.draw_string_2d(10, 195, 1, 1, "yellow", self.renderer.yellow())
                self.renderer.draw_string_2d(10, 210, 1, 1, "lime", self.renderer.lime())
                self.renderer.draw_string_2d(10, 225, 1, 1, "green", self.renderer.green())
                self.renderer.draw_string_2d(10, 240, 1, 1, "cyan", self.renderer.cyan())
                self.renderer.draw_string_2d(10, 255, 1, 1, "teal", self.renderer.teal())
                self.renderer.draw_string_2d(10, 270, 1, 1, "blue", self.renderer.blue())
                self.renderer.draw_string_2d(10, 285, 1, 1, "pink", self.renderer.pink())
                self.renderer.draw_string_2d(10, 300, 1, 1, "purple", self.renderer.purple())
            self.renderer.end_rendering()

        if my_car.physics.location.z > 50:
            self.cleared = True
        else:
            self.cleared = False

    def do_dropshot_tile_test(self, game_tick_packet: GameTickPacket):
        num_tiles = game_tick_packet.num_tiles
        self.renderer.begin_rendering(group_id="dropshot")
        self.renderer.draw_string_2d(10, 10, 2, 2, 'num tiles: ' + str(num_tiles), self.renderer.white())
        if num_tiles > 0:
            num_filled = 0
            num_damaged = 0
            num_open = 0
            num_unknown = 0
            field_info = self.get_field_info()
            red = self.renderer.create_color(255, 255, 60, 60)
            green = self.renderer.create_color(255, 60, 255, 60)
            for i in range(num_tiles):
                tile = game_tick_packet.dropshot_tiles[i]
                location = field_info.goals[i].location
                if tile.tile_state == DropshotTileState.UNKNOWN:
                    num_unknown += 1
                if tile.tile_state == DropshotTileState.FILLED:
                    num_filled += 1
                if tile.tile_state == DropshotTileState.DAMAGED:
                    self.renderer.draw_rect_3d(location, 5, 5, True, green, True)
                    num_damaged += 1
                if tile.tile_state == DropshotTileState.OPEN:
                    self.renderer.draw_line_2d_3d(0, 0, location, red)
                    num_open += 1

            self.renderer.draw_string_2d(10, 30, 2, 2, 'num filled: ' + str(num_filled), self.renderer.white())
            self.renderer.draw_string_2d(10, 50, 2, 2, 'num damaged: ' + str(num_damaged), self.renderer.white())
            self.renderer.draw_string_2d(10, 70, 2, 2, 'num open: ' + str(num_open), self.renderer.white())
            self.renderer.draw_string_2d(10, 90, 2, 2, 'num unknown: ' + str(num_unknown), self.renderer.white())

            absorbed_force = game_tick_packet.game_ball.drop_shot_info.absorbed_force
            self.renderer.draw_string_2d(10, 110, 2, 2, 'absorbed force: ' + str(absorbed_force), self.renderer.white())

            damage_index = game_tick_packet.game_ball.drop_shot_info.damage_index
            self.renderer.draw_string_2d(10, 130, 2, 2, 'damage index: ' + str(damage_index), self.renderer.white())

            force_accum_recent = game_tick_packet.game_ball.drop_shot_info.force_accum_recent
            self.renderer.draw_string_2d(10, 150, 2, 2, 'force accum recent: ' +
                                         str(force_accum_recent), self.renderer.white())

        self.renderer.end_rendering()

    def set_state_test(self, game_tick_packet: GameTickPacket):

        my_car = game_tick_packet.game_cars[self.index]
        car_location = my_car.physics.location

        car_state = CarState()
        if math.fabs(car_location.x) > 2000 and car_location.z < 100:
            car_state = CarState(
                Physics(velocity=Vector3(z=500, x=-car_location.x * .5), rotation=Rotator(math.pi / 2, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)),
                jumped=False, double_jumped=False, boost_amount=87)

        ball_phys = game_tick_packet.game_ball.physics
        ball_state = BallState()
        if ball_phys.location.z < 500:
            ball_state = BallState(Physics(location=Vector3(0, 0, 800), velocity=Vector3(0, 0, 1000)))

        if math.fabs(car_location.x) > 1000:
            boost_states = {i: BoostState(1.0) for i in range(34)}
        else:
            boost_states = {i: BoostState(0.0) for i in range(34)}

        game_info_state = GameInfoState(world_gravity_z=-(ball_phys.location.z - 1200), game_speed=0.5)

        game_state = GameState(ball=ball_state, cars={self.index: car_state},
                               boosts=boost_states, game_info=game_info_state)
        self.set_game_state(game_state)

    def render_ball_prediction(self):
        ball_prediction = self.get_ball_prediction_struct()

        if ball_prediction is not None:

            self.renderer.begin_rendering('prediction')
            colors = self.setup_rainbow()
            for i in range(5, ball_prediction.num_slices, 5):
                current_slice = ball_prediction.slices[i].physics.location
                self.renderer.draw_rect_3d(current_slice, 8, 8, True, colors[i % len(colors)], True)
            self.renderer.end_rendering()

    def do_physics_tick_test(self, game_tick_packet: GameTickPacket) -> None:
        self.renderer.begin_rendering('physics_tick_test')
        color = self.renderer.white()
        cur_y = 200

        def dump(text: str) -> None:
            nonlocal cur_y
            self.renderer.draw_string_2d(10, cur_y, 2, 2, text, color)
            cur_y += 25

        tick = self.get_rigid_body_tick()
        ball_state = tick.ball.state
        car_state = tick.players[0].state
        car_input = tick.players[0].input
        dump(f'tick time: {game_tick_packet.game_info.seconds_elapsed}')
        dump(f'ball frame: {ball_state.frame}')
        dump(f'ball loc x: {ball_state.location.x}')
        dump(f'ball quat x: {ball_state.rotation.x}')
        dump(f'ball vel x: {ball_state.velocity.x}')
        dump(f'ball ang vel x: {ball_state.angular_velocity.x}')
        dump(f'car frame: {car_state.frame}')
        dump(f'car loc x: {car_state.location.x}')
        dump(f'car quat x: {car_state.rotation.x}')

        q = car_state.rotation
        dump(f'car quat mag: {math.sqrt(q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w)}')
        dump(f'car vel x: {car_state.velocity.x}')
        dump(f'car ang vel x: {car_state.angular_velocity.x}')
        dump(f'car steer: {car_input.steer}')

        self.renderer.end_rendering()

    def setup_rainbow(self):
        return [
            self.renderer.create_color(255, 255, 100, 100),
            self.renderer.create_color(255, 255, 255, 100),
            self.renderer.create_color(255, 100, 255, 100),
            self.renderer.create_color(255, 100, 255, 255),
            self.renderer.create_color(255, 100, 100, 255),
            self.renderer.create_color(255, 255, 100, 255)
        ]

    def handle_quick_chat(self, index, team, quick_chat):
        self.logger.info(f"Got quickchat: {quick_chat} from player index {index} on team {team}")

    def load_config(self, config_header):
        self.flip_turning = config_header.getboolean('flip_turning')
        self.test_rendering = config_header.getboolean('test_rendering')
        self.test_quickchat = config_header.getboolean('test_quickchat')
        self.test_dropshot = config_header.getboolean('test_dropshot')
        self.test_state = config_header.getboolean('test_state')
        self.test_ball_prediction = config_header.getboolean('test_ball_prediction')
        self.test_physics_tick = config_header.getboolean('test_physics_tick')

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('flip_turning', bool, default=False, description='if true bot will turn opposite way')
        params.add_value('test_rendering', bool, default=False, description='if true bot will render random stuff')
        params.add_value('test_quickchat', bool, default=False, description='if true bot will spam quickchats')
        params.add_value('test_dropshot', bool, default=False, description='if true bot will render dropshot info')
        params.add_value('test_state', bool, default=False, description='if true bot will alter its game state')
        params.add_value('test_ball_prediction', bool, default=False,
                         description='if true bot will render ball prediction')
        params.add_value('test_physics_tick', bool, default=False,
                         description='if true bot will render ball prediction')


class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vector2(self.x + val.x, self.y + val.y)

    def __sub__(self, val):
        return Vector2(self.x - val.x, self.y - val.y)

    def correction_to(self, ideal):
        # The in-game axes are left handed, so use -x
        current_in_radians = math.atan2(self.y, -self.x)
        ideal_in_radians = math.atan2(ideal.y, -ideal.x)

        correction = ideal_in_radians - current_in_radians

        # Make sure we go the 'short way'
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * math.pi
            else:
                correction -= 2 * math.pi

        return correction


def get_car_facing_vector(car):
    pitch = float(car.physics.rotation.pitch)
    yaw = float(car.physics.rotation.yaw)

    facing_x = math.cos(pitch) * math.cos(yaw)
    facing_y = math.cos(pitch) * math.sin(yaw)

    return Vector2(facing_x, facing_y)
