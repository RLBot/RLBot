from dataclasses import dataclass

def cleanup_zombie_flatbuffers():
    try:
        from flatbuffers import Builder
    except ModuleNotFoundError as e:
        import psutil
        from pathlib import Path
        from shutil import rmtree
        flatbuffers_path = Path(psutil.__path__[0]).parent / 'flatbuffers-1.9.dist-info'
        if flatbuffers_path.exists():
            print("Removing flatbuffers dist-info folder.")
            for i in range(10):
                print("################################################")
            print("HELLO RLBOT USER, please try launching again, it will probably work next time!")
            rmtree(str(flatbuffers_path))
            exit(1)
        else:
            print(f"Path {flatbuffers_path} did not exist.")
            raise e
cleanup_zombie_flatbuffers()

from flatbuffers import Builder
from rlbot.messages.flat import LoadoutPaint, PlayerLoadout, Color as FlatColor
from rlbot.utils.structures.start_match_structures import PlayerConfiguration
from rlbot.utils.structures.start_match_structures import Color as ColorStruct


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
        self.primary_color_lookup: Color = None
        self.secondary_color_lookup: Color = None

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

        if self.primary_color_lookup:
            player_configuration.use_rgb_lookup = True
            self.primary_color_lookup.write(player_configuration.primary_color_lookup)

        if self.secondary_color_lookup:
            player_configuration.use_rgb_lookup = True
            self.secondary_color_lookup.write(player_configuration.secondary_color_lookup)

    def write_to_flatbuffer(self, builder: Builder):
        if self.paint_config:
            paint_offset = self.paint_config.write_to_flatbuffer(builder)

        if self.primary_color_lookup:
            primary_color_offset = self.primary_color_lookup.write_to_flatbuffer(builder)
        if self.secondary_color_lookup:
            secondary_color_offset = self.secondary_color_lookup.write_to_flatbuffer(builder)

        PlayerLoadout.PlayerLoadoutStart(builder)
        PlayerLoadout.PlayerLoadoutAddTeamColorId(builder, self.team_color_id)
        PlayerLoadout.PlayerLoadoutAddCustomColorId(builder, self.custom_color_id)
        PlayerLoadout.PlayerLoadoutAddCarId(builder, self.car_id)
        PlayerLoadout.PlayerLoadoutAddDecalId(builder, self.decal_id)
        PlayerLoadout.PlayerLoadoutAddWheelsId(builder, self.wheels_id)
        PlayerLoadout.PlayerLoadoutAddBoostId(builder, self.boost_id)
        PlayerLoadout.PlayerLoadoutAddAntennaId(builder, self.antenna_id)
        PlayerLoadout.PlayerLoadoutAddHatId(builder, self.hat_id)
        PlayerLoadout.PlayerLoadoutAddPaintFinishId(builder, self.paint_finish_id)
        PlayerLoadout.PlayerLoadoutAddCustomFinishId(builder, self.custom_finish_id)
        PlayerLoadout.PlayerLoadoutAddEngineAudioId(builder, self.engine_audio_id)
        PlayerLoadout.PlayerLoadoutAddTrailsId(builder, self.trails_id)
        PlayerLoadout.PlayerLoadoutAddGoalExplosionId(builder, self.goal_explosion_id)
        if self.paint_config:
            PlayerLoadout.PlayerLoadoutAddLoadoutPaint(builder, paint_offset)
        if self.primary_color_lookup:
            PlayerLoadout.PlayerLoadoutAddPrimaryColorLookup(builder, primary_color_offset)
        if self.secondary_color_lookup:
            PlayerLoadout.PlayerLoadoutAddSecondaryColorLookup(builder, secondary_color_offset)
        return PlayerLoadout.PlayerLoadoutEnd(builder)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

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

    def write_to_flatbuffer(self, builder: Builder):
        paint = self
        LoadoutPaint.LoadoutPaintStart(builder)
        if paint:
            LoadoutPaint.LoadoutPaintAddCarPaintId(builder, paint.car_paint_id)
            LoadoutPaint.LoadoutPaintAddDecalPaintId(builder, paint.decal_paint_id)
            LoadoutPaint.LoadoutPaintAddWheelsPaintId(builder, paint.wheels_paint_id)
            LoadoutPaint.LoadoutPaintAddBoostPaintId(builder, paint.boost_paint_id)
            LoadoutPaint.LoadoutPaintAddAntennaPaintId(builder, paint.antenna_paint_id)
            LoadoutPaint.LoadoutPaintAddHatPaintId(builder, paint.hat_paint_id)
            LoadoutPaint.LoadoutPaintAddTrailsPaintId(builder, paint.trails_paint_id)
            LoadoutPaint.LoadoutPaintAddGoalExplosionPaintId(builder, paint.goal_explosion_paint_id)
        return LoadoutPaint.LoadoutPaintEnd(builder)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__


@dataclass
class Color:
    red: int
    green: int
    blue: int
    alpha: int

    def write(self, color: ColorStruct):
        color.r = self.red
        color.g = self.green
        color.b = self.blue
        color.a = self.alpha

    def write_to_flatbuffer(self, builder: Builder):
        FlatColor.ColorStart(builder)
        FlatColor.ColorAddR(builder, self.red)
        FlatColor.ColorAddG(builder, self.green)
        FlatColor.ColorAddB(builder, self.blue)
        FlatColor.ColorAddA(builder, self.alpha)
        return FlatColor.ColorEnd(builder)



