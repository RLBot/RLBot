import ctypes
import hashlib

import flatbuffers
from rlbot.utils.structures.game_status import RLBotCoreStatus
from rlbot.utils.structures.game_data_struct import Vector3 as GameDataStructVector3
from rlbot.utils.logging_utils import get_logger

from rlbot.messages.flat import RenderGroup
from rlbot.messages.flat import Color
from rlbot.messages.flat import RenderMessage
from rlbot.messages.flat import Vector3
from rlbot.messages.flat import Float
from rlbot.messages.flat.RenderType import RenderType


MAX_INT = 2147483647 // 2


class RenderingManager:
    """
    Manages rendering and statefully bundles rendering into a group, can only render one group at a time.
    """
    renderGroup = None
    render_state = False
    builder = None
    render_list = []
    group_id = None
    bot_index = 0
    bot_team = 0

    def setup_function_types(self, dll_instance):
        self.renderGroup = dll_instance.RenderGroup

        self.renderGroup.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.renderGroup.restype = ctypes.c_int

    def set_bot_index_and_team(self, bot_index=0, bot_team=0):
        self.bot_index = bot_index
        self.bot_team = bot_team

    def send_group(self, buffer):
        rlbot_status = self.renderGroup(bytes(buffer), len(buffer))
        if rlbot_status != RLBotCoreStatus.Success:
            get_logger("Renderer").error("bad status %s", RLBotCoreStatus.status_list[rlbot_status])

    def begin_rendering(self, group_id='default'):
        self.group_id = group_id
        self.builder = flatbuffers.Builder(0)
        self.render_list = []
        self.render_state = True

    def end_rendering(self):
        self.render_state = False
        if self.group_id is None:
            self.group_id = 'default'

        group_id = str(self.bot_index) + str(self.group_id)
        group_id_hashed = int(hashlib.sha256(str(group_id).encode('utf-8')).hexdigest(), 16) % MAX_INT

        list_length = len(self.render_list)

        RenderGroup.RenderGroupStartRenderMessagesVector(self.builder, list_length)

        for i in reversed(range(0, list_length)):
            self.builder.PrependUOffsetTRelative(self.render_list[i])

        messages = self.builder.EndVector(list_length)

        RenderGroup.RenderGroupStart(self.builder)
        RenderGroup.RenderGroupAddId(self.builder, group_id_hashed)
        RenderGroup.RenderGroupAddRenderMessages(self.builder, messages)
        result = RenderGroup.RenderGroupEnd(self.builder)

        self.builder.Finish(result)

        buf = self.builder.Output()
        self.send_group(buf)

    def clear_screen(self, group_id='default'):
        self.begin_rendering(group_id)
        self.end_rendering()

    def is_rendering(self):
        return self.render_state

    def draw_line_2d(self, x1, y1, x2, y2, color):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawLine2D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(x1, y1))
        RenderMessage.RenderMessageAddEnd(messageBuilder, self.__create_vector(x2, y2))
        message = RenderMessage.RenderMessageEnd(messageBuilder)

        self.render_list.append(message)
        return self

    def draw_polyline_2d(self, vectors, color):
        if len(vectors) < 2:
            get_logger("Renderer").error("draw_polyline_2d requires atleast 2 vectors!")
            return self
        
        messageBuilder = self.builder

        for i in range(0, len(vectors)-1):
            RenderMessage.RenderMessageStart(messageBuilder)
            RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawLine2D)
            RenderMessage.RenderMessageAddColor(messageBuilder, color)
            RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(vectors[i]))
            RenderMessage.RenderMessageAddEnd(messageBuilder, self.__create_vector(vectors[i+1]))
            message = RenderMessage.RenderMessageEnd(messageBuilder)
            self.render_list.append(message)

        return self

    def draw_line_3d(self, vec1, vec2, color):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawLine3D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(vec1))
        RenderMessage.RenderMessageAddEnd(messageBuilder, self.__create_vector(vec2))
        message = RenderMessage.RenderMessageEnd(messageBuilder)

        self.render_list.append(message)
        return self

    def draw_polyline_3d(self, vectors, color):
        if len(vectors) < 2:
            get_logger("Renderer").error("draw_polyline_3d requires atleast 2 vectors!")
            return self

        messageBuilder = self.builder

        for i in range(0, len(vectors)-1):
            RenderMessage.RenderMessageStart(messageBuilder)
            RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawLine3D)
            RenderMessage.RenderMessageAddColor(messageBuilder, color)
            RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(vectors[i]))
            RenderMessage.RenderMessageAddEnd(messageBuilder, self.__create_vector(vectors[i+1]))
            message = RenderMessage.RenderMessageEnd(messageBuilder)
            self.render_list.append(message)

        return self

    def draw_line_2d_3d(self, x, y, vec, color):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawLine2D_3D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(x, y))
        RenderMessage.RenderMessageAddEnd(messageBuilder, self.__create_vector(vec))
        message = RenderMessage.RenderMessageEnd(messageBuilder)

        self.render_list.append(message)
        return self

    def draw_rect_2d(self, x, y, width, height, filled, color):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawRect2D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(x, y))
        RenderMessage.RenderMessageAddScaleX(messageBuilder, width)
        RenderMessage.RenderMessageAddScaleY(messageBuilder, height)
        RenderMessage.RenderMessageAddIsFilled(messageBuilder, filled)
        message = RenderMessage.RenderMessageEnd(messageBuilder)

        self.render_list.append(message)
        return self

    def draw_rect_3d(self, vec, width, height, filled, color, centered=False):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(
            messageBuilder,
            RenderType.DrawCenteredRect3D if centered else RenderType.DrawRect3D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(vec))
        RenderMessage.RenderMessageAddScaleX(messageBuilder, width)
        RenderMessage.RenderMessageAddScaleY(messageBuilder, height)
        RenderMessage.RenderMessageAddIsFilled(messageBuilder, filled)
        message = RenderMessage.RenderMessageEnd(messageBuilder)

        self.render_list.append(message)
        return self

    def draw_string_2d(self, x, y, scale_x, scale_y, text, color):
        messageBuilder = self.builder
        builtString = messageBuilder.CreateString(text)

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawString2D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(x, y))
        RenderMessage.RenderMessageAddScaleX(messageBuilder, scale_x)
        RenderMessage.RenderMessageAddScaleY(messageBuilder, scale_y)
        RenderMessage.RenderMessageAddText(messageBuilder, builtString)
        message = RenderMessage.RenderMessageEnd(messageBuilder)

        self.render_list.append(message)
        return self

    def draw_string_3d(self, vec, scale_x, scale_y, text, color):
        messageBuilder = self.builder
        builtString = messageBuilder.CreateString(text)

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawString3D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(vec))
        RenderMessage.RenderMessageAddScaleX(messageBuilder, scale_x)
        RenderMessage.RenderMessageAddScaleY(messageBuilder, scale_y)
        RenderMessage.RenderMessageAddText(messageBuilder, builtString)
        message = RenderMessage.RenderMessageEnd(messageBuilder)

        self.render_list.append(message)
        return self

    def create_color(self, alpha, red, green, blue):
        colorBuilder = self.builder
        # Color.CreateColor(colorBuilder, alpha, red, green, blue)
        Color.ColorStart(colorBuilder)
        Color.ColorAddA(colorBuilder, alpha)
        Color.ColorAddR(colorBuilder, red)
        Color.ColorAddG(colorBuilder, green)
        Color.ColorAddB(colorBuilder, blue)
        return Color.ColorEnd(colorBuilder)

    def black(self):
        return self.create_color(255, 0, 0, 0)

    def white(self):
        return self.create_color(255, 255, 255, 255)

    def gray(self):
        return self.create_color(255, 128, 128, 128)

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

    """Supports Flatbuffers Vector3, cTypes Vector3, list/tuple of numbers, or passing x,y,z (z optional)"""
    def __create_vector(self, *vec):
        import numbers

        if len(vec) == 1:
            if isinstance(vec[0], list) or isinstance(vec[0], tuple):
                if 1 < len(vec[0]) <= 3:
                    if isinstance(vec[0][0], numbers.Number) and isinstance(vec[0][1], numbers.Number):
                        x = vec[0][0]
                        y = vec[0][1]
                    else:
                        raise ValueError(
                            "Unexpected type(s) for creating vector: {0}, {1}".format(type(vec[0][1]), type(vec[0][1])))
                    if len(vec[0]) == 2:
                        z = 0
                    else:
                        if isinstance(vec[0][2], numbers.Number):
                            z = vec[0][2]
                        else:
                            raise ValueError("Unexpected type for creating vector: {0}".format(type(vec[0][2])))
                else:
                    raise ValueError("Unexpected list/tuple length for creating vector: {0}".format(len(vec)))
            elif isinstance(vec[0], Vector3.Vector3):
                x = vec[0].X()
                y = vec[0].Y()
                z = vec[0].Z()
            elif isinstance(vec[0], GameDataStructVector3):
                x = vec[0].x
                y = vec[0].y
                z = vec[0].z
            elif type(vec[0]).__name__ == 'vec3': #Support Chip's LinearAlgebra.vec3
                x = vec[0][0]
                y = vec[0][1]
                z = vec[0][2]
            else:
                raise ValueError("Unexpected type for creating vector: {0}".format(type(vec[0])))
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
                        raise ValueError("Unexpected type for creating vector: {0}".format(type(vec[0])))
            else:
                raise ValueError("Unexpected type(s) for creating vector: {0}, {1}".format(type(vec[0]), type(vec[1])))
        else:
            raise ValueError("Unexpected number of arguments for creating vector")

        return Vector3.CreateVector3(self.builder, x, y, z)
