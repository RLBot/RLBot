import ctypes
import hashlib
from typing import Optional, Set

from rlbot.utils.structures.game_data_struct import Vector3
from rlbot.utils.structures.struct import Struct
from rlbot.utils.logging_utils import get_logger

class Color(Struct):
    _fields_ = [("r", ctypes.c_ubyte),
                ("g", ctypes.c_ubyte),
                ("b", ctypes.c_ubyte),
                ("a", ctypes.c_ubyte)]


MAX_INT = 2147483647 // 2

DEFAULT_GROUP_ID = 'default'

class RenderingManager:
    def __init__(self):
        self.renderGroup = None
        self.render_state = False
        self.builder = None
        self.render_list = []
        self.bot_index = 0
        self.bot_team = 0
        self.group_id: Optional[str] = None
        self.touched_group_ids: Set[str] = set()

        self.native_constructor = None
        self.native_destructor = None
        self.native_finish_and_send = None
        self.native_draw_line_3d = None
        self.native_draw_polyline_2d = None
        self.native_draw_string_2d = None
        self.native_draw_string_3d = None
        self.native_draw_rect_2d = None
        self.native_draw_rect_3d = None

    def setup_function_types(self, dll_instance):
        self.native_constructor = dll_instance.Renderer_Constructor
        self.native_constructor.argtypes = [ctypes.c_int]
        self.native_constructor.restype = ctypes.c_void_p

        self.native_destructor = dll_instance.Renderer_Destructor
        self.native_destructor.argtypes = [ctypes.c_void_p]

        self.native_finish_and_send = dll_instance.Renderer_FinishAndSend
        self.native_finish_and_send.argtypes = [ctypes.c_void_p]

        self.native_draw_line_3d = dll_instance.Renderer_DrawLine3D
        self.native_draw_line_3d.argtypes = [ctypes.c_void_p, Color, Vector3, Vector3]

        self.native_draw_polyline_3d = dll_instance.Renderer_DrawPolyLine3D
        self.native_draw_polyline_3d.argtypes = [ctypes.c_void_p, Color, ctypes.POINTER(Vector3), ctypes.c_int]

        self.native_draw_string_2d = dll_instance.Renderer_DrawString2D
        self.native_draw_string_2d.argtypes = [ctypes.c_void_p, ctypes.c_char_p, Color, Vector3, ctypes.c_int, ctypes.c_int]

        self.native_draw_string_3d = dll_instance.Renderer_DrawString3D
        self.native_draw_string_3d.argtypes = [ctypes.c_void_p, ctypes.c_char_p, Color, Vector3, ctypes.c_int, ctypes.c_int]

        self.native_draw_rect_2d = dll_instance.Renderer_DrawRect2D
        self.native_draw_rect_2d.argtypes = [ctypes.c_void_p, Color, Vector3, ctypes.c_int, ctypes.c_int, ctypes.c_bool]

        self.native_draw_rect_3d = dll_instance.Renderer_DrawRect3D
        self.native_draw_rect_3d.argtypes = [ctypes.c_void_p, Color, Vector3, ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool]

    def set_bot_index_and_team(self, bot_index=0, bot_team=0):
        self.bot_index = bot_index
        self.bot_team = bot_team

    def send_group(self, buffer):
        rlbot_status = self.renderGroup(bytes(buffer), len(buffer))
        if rlbot_status != RLBotCoreStatus.Success:
            get_logger("Renderer").error("bad status %s", RLBotCoreStatus.status_list[rlbot_status])

    def begin_rendering(self, group_id: str=DEFAULT_GROUP_ID):
        self.touched_group_ids.add(group_id)
        self.group_id = group_id
        self.render_list = []
        self.render_state = True

        if self.group_id is None:
            self.group_id = DEFAULT_GROUP_ID

        group_id = str(self.bot_index) + str(self.group_id)
        group_id_hashed = int(hashlib.sha256(str(group_id).encode('utf-8')).hexdigest(), 16) % MAX_INT

        # Prevent memory leak
        if self.builder is not None:
            self.native_destructor(self.builder)

        self.builder = self.native_constructor(group_id_hashed)


    def end_rendering(self):
        if self.builder is not None:
            self.native_finish_and_send(self.builder)
            self.native_destructor(self.builder)
        self.builder = None
        
        self.render_state = False

    def clear_screen(self, group_id: str=DEFAULT_GROUP_ID):
        self.begin_rendering(group_id)
        self.end_rendering()

    def clear_all_touched_render_groups(self):
        """
        Clears all render groups which have been drawn to using `begin_rendering(group_id)`.
        Note: This does not clear render groups created by e.g. other bots.
        """
        for group_id in self.touched_group_ids:
            self.clear_screen(group_id)

    def is_rendering(self):
        return self.render_state

    def draw_line_2d(self, x1, y1, x2, y2, color):
        get_logger("Renderer").error("draw_line_2d is not supported!")
        return self

    def draw_polyline_2d(self, vectors, color):
        if len(vectors) < 2:
            get_logger("Renderer").error("draw_polyline_2d requires atleast 2 vectors!")
            return self

        get_logger("Renderer").error("draw_polyline_2d is not supported!")
        return self

    def draw_line_3d(self, vec1, vec2, color):
        if self.builder is None:
            get_logger("Renderer").error("Use begin_rendering before using any of the drawing functions!")
            return self

        self.native_draw_line_3d(self.builder, color, self.__create_vector(vec1), self.__create_vector(vec2))
        return self

    def draw_polyline_3d(self, vectors, color):
        if len(vectors) < 2:
            get_logger("Renderer").error("draw_polyline_3d requires atleast 2 vectors!")
            return self

        if self.builder is None:
            get_logger("Renderer").error("Use begin_rendering before using any of the drawing functions!")
            return self
        
        # TODO: would be nice to use a native function
        for i in range(len(vectors) - 1):
            self.draw_line_3d(vectors[i], vectors[i+1], color)

        return self

    def draw_line_2d_3d(self, x, y, vec, color):
        get_logger("Renderer").error("draw_line_2d_3d is not supported!")
        return self

    def draw_rect_2d(self, x, y, width, height, filled, color):
        if self.builder is None:
            get_logger("Renderer").error("Use begin_rendering before using any of the drawing functions!")
            return self
        self.native_draw_rect_2d(self.builder, color, self.__create_vector([x,y,0]), width, height, filled)
        return self

    def draw_rect_3d(self, vec, width, height, filled, color, centered=False):
        if self.builder is None:
            get_logger("Renderer").error("Use begin_rendering before using any of the drawing functions!")
            return self
        self.native_draw_rect_3d(self.builder, color, self.__create_vector(vec), width, height, filled, centered)
        return self

    def draw_string_2d(self, x, y, scale_x, scale_y, text, color):
        if self.builder is None:
            get_logger("Renderer").error("Use begin_rendering before using any of the drawing functions!")
            return self
        self.native_draw_string_2d(self.builder, text.encode('utf-8'), color, self.__create_vector([x,y,0]), scale_x, scale_y)
        return self

    def draw_string_3d(self, vec, scale_x, scale_y, text, color):
        if self.builder is None:
            get_logger("Renderer").error("Use begin_rendering before using any of the drawing functions!")
            return self
        self.native_draw_string_3d(self.builder, text.encode('utf-8'), color, self.__create_vector(vec), scale_x, scale_y)
        return self

    def create_color(self, alpha, red, green, blue):
        return Color(red, green, blue, alpha)

    def black(self):
        return self.create_color(255, 0, 0, 0)

    def white(self):
        return self.create_color(255, 255, 255, 255)

    def gray(self):
        return self.create_color(255, 128, 128, 128)

    def grey(self):
        return self.gray()

    def blue(self):
        return self.create_color(255, 0, 0, 255)

    def red(self):
        return self.create_color(255, 255, 0, 0)

    def green(self):
        return self.create_color(255, 0, 128, 0)

    def lime(self):
        return self.create_color(255, 0, 255, 0)

    def yellow(self):
        return self.create_color(255, 255, 255, 0)

    def orange(self):
        return self.create_color(255, 225, 128, 0)

    def cyan(self):
        return self.create_color(255, 0, 255, 255)

    def pink(self):
        return self.create_color(255, 255, 0, 255)

    def purple(self):
        return self.create_color(255, 128, 0, 128)

    def teal(self):
        return self.create_color(255, 0, 128, 128)

    def team_color(self, team=None, alt_color=False):
        """
        Returns the team color of the bot. Team 0: blue, team 1: orange, other: white
        :param team: Specify which team's color. If None, the associated bot's team color will be returned.
        :param alt_color: If True, returns the alternate team colors instead. Team 0: cyan, team 1: red, other: gray
        :return: a team color
        """
        if team is None:
            team = self.bot_team

        if team == 0:
            return self.cyan() if alt_color else self.blue()
        elif team == 1:
            return self.red() if alt_color else self.orange()
        else:
            return self.gray() if alt_color else self.white()

    def get_rendering_manager(self, bot_index=0, bot_team=0):
        """
        Gets all the raw render functions but without giving access to any internal logic or the dll
        :return: An object with the same interface as the functions above
        """
        self.set_bot_index_and_team(bot_index, bot_team)
        return self

    def __wrap_float(self, number):
        return Float.CreateFloat(self.builder, number)

    def __create_vector(self, *vec) -> Vector3:
        """
        Converts a variety of vector types to a flatbuffer Vector3.
        Supports Flatbuffers Vector3, cTypes Vector3, list/tuple of numbers, or passing x,y,z (z optional)
        """
        import numbers

        if len(vec) == 1:
            if hasattr(vec[0], "__getitem__"):  # Support all subscriptable types.
                try:
                    x = float(vec[0][0])
                    y = float(vec[0][1])
                    try:
                        z = float(vec[0][2])
                    except (ValueError, IndexError):
                        z = 0
                except ValueError:
                    raise ValueError(f"Unexpected type(s) for creating vector: {type(vec[0][0])}, {type(vec[0][1])}")
                except IndexError:
                    raise IndexError(f"Unexpected IndexError when creating vector from type: {type(vec[0])}")
            #elif isinstance(vec[0], Vector3.Vector3):
            #    x = vec[0].X()
            #    y = vec[0].Y()
            #    z = vec[0].Z()
            elif isinstance(vec[0], Vector3):
                x = vec[0].x
                y = vec[0].y
                z = vec[0].z
            else:
                raise ValueError(f"Unexpected type for creating vector: {type(vec[0])}")
        elif len(vec) == 2 or len(vec) == 3:
            if isinstance(vec[0], numbers.Number) and isinstance(vec[1], numbers.Number):
                x = vec[0]
                y = vec[1]
                if len(vec) == 2:
                    z = 0
                else:
                    if isinstance(vec[2], numbers.Number):
                        z = vec[2]
                    else:
                        raise ValueError(f"Unexpected type for creating vector: {type(vec[0])}")
            else:
                raise ValueError(f"Unexpected type(s) for creating vector: {type(vec[0])}, {type(vec[1])}")
        else:
            raise ValueError("Unexpected number of arguments for creating vector")

        return Vector3(x, y, z)


class DummyRenderer(RenderingManager):

    def __init__(self, renderer):
        self.renderGroup = renderer.renderGroup
        self.render_state = renderer.render_state
        self.builder = renderer.builder
        self.render_list = renderer.render_list
        self.group_id = renderer.group_id
        self.bot_index = renderer.bot_index
        self.bot_team = renderer.bot_team

    def clear_screen(self, group_id='default'):
        pass

    def draw_line_2d(self, x1, y1, x2, y2, color):
        return self

    def draw_polyline_2d(self, vectors, color):
        return self

    def draw_line_3d(self, vec1, vec2, color):
        return self

    def draw_polyline_3d(self, vectors, color):
        return self

    def draw_line_2d_3d(self, x, y, vec, color):
        return self

    def draw_rect_2d(self, x, y, width, height, filled, color):
        return self

    def draw_rect_3d(self, vec, width, height, filled, color, centered=False):
        return self

    def draw_string_2d(self, x, y, scale_x, scale_y, text, color):
        return self

    def draw_string_3d(self, vec, scale_x, scale_y, text, color):
        return self

    def begin_rendering(self, group_id='default'):
        self.builder = flatbuffers.Builder(0)

    def end_rendering(self):
        pass

    def clear_all_touched_render_groups(self):
        pass
