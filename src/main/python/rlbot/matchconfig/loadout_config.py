from rlbot.utils.structures.start_match_structures import PlayerConfiguration


class LoadoutConfig:
    def __init__(self):
        self.team_color_id: int = 0
        self.custom_color_id: int = 0
        self.car_id: int = 0
        self.decal_id: int = 0
        self.wheels_id: int = 0
        self.boost_id: int = 0
        self.antenna_id: int = 0
        self.hat_id: int = 0
        self.paint_finish_id: int = 0
        self.custom_finish_id: int = 0
        self.engine_audio_id: int = 0
        self.trails_id: int = 0
        self.goal_explosion_id: int = 0
        self.paint_config: LoadoutPaintConfig = LoadoutPaintConfig()

    def write(self, player_configuration: PlayerConfiguration):
        player_configuration.team_color_id = self.team_color_id
        player_configuration.custom_color_id = self.custom_color_id
        player_configuration.car_id = self.car_id
        player_configuration.decal_id = self.decal_id
        player_configuration.wheels_id = self.wheels_id
        player_configuration.boost_id = self.boost_id
        player_configuration.antenna_id = self.antenna_id
        player_configuration.hat_id = self.hat_id
        player_configuration.paint_finish_id = self.paint_finish_id
        player_configuration.custom_finish_id = self.custom_finish_id
        player_configuration.engine_audio_id = self.engine_audio_id
        player_configuration.trails_id = self.trails_id
        player_configuration.goal_explosion_id = self.goal_explosion_id

        if self.paint_config:
            self.paint_config.write(player_configuration)


class LoadoutPaintConfig:
    def __init__(self):
        self.car_paint_id: int = 0
        self.decal_paint_id: int = 0
        self.wheels_paint_id: int = 0
        self.boost_paint_id: int = 0
        self.antenna_paint_id: int = 0
        self.hat_paint_id: int = 0
        self.trails_paint_id: int = 0
        self.goal_explosion_paint_id: int = 0

    def write(self, player_configuration: PlayerConfiguration):
        player_configuration.car_paint_id = self.car_paint_id
        player_configuration.decal_paint_id = self.decal_paint_id
        player_configuration.wheels_paint_id = self.wheels_paint_id
        player_configuration.boost_paint_id = self.boost_paint_id
        player_configuration.antenna_paint_id = self.antenna_paint_id
        player_configuration.hat_paint_id = self.hat_paint_id
        player_configuration.trails_paint_id = self.trails_paint_id
        player_configuration.goal_explosion_paint_id = self.goal_explosion_paint_id
