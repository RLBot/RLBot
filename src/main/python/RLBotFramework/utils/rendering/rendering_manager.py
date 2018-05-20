import ctypes
import flatbuffers
import hashlib

from RLBotFramework.utils.structures.game_status import RLBotCoreStatus
from RLBotFramework.utils.logging_utils import get_logger

from RLBotMessages.flat import RenderGroup
from RLBotMessages.flat import Color
from RLBotMessages.flat import RenderMessage
from RLBotMessages.flat import Vector3
from RLBotMessages.flat import Float
from RLBotMessages.flat.RenderType import RenderType


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

    def __init__(self):
        self.ignored_funcs = ['setup_function_types', 'get_render_functions',
                              'create_dynamic_function', 'send_group']

    def setup_function_types(self, dll_instance):
        self.renderGroup = dll_instance.RenderGroup

        self.renderGroup.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.renderGroup.restype = ctypes.c_int

    def set_bot_index(self, bot_index=0):
        self.bot_index = bot_index

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

    def draw_line_3d(self, vec1, vec2, color):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawLine3D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(*vec1))
        RenderMessage.RenderMessageAddEnd(messageBuilder, self.__create_vector(*vec2))
        message = RenderMessage.RenderMessageEnd(messageBuilder)

        self.render_list.append(message)
        return self

    def draw_line_2d_3d(self, x, y, vec, color):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawLine2D_3D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(x, y))
        RenderMessage.RenderMessageAddEnd(messageBuilder, self.__create_vector(*vec))
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

    def draw_rect_3d(self, vec, width, height, filled, color):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawRect3D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(*vec))
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
        RenderMessage.RenderMessageAddStart(messageBuilder, self.__create_vector(*vec))
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

    def get_render_functions(self):
        """
        Gets all the raw render functions but without giving access to any internal logic or the dll
        :return: An object with the same interface as the functions above
        """

        return self

    def __wrap_float(self, number):
        return Float.CreateFloat(self.builder, number)

    def __create_vector(self, x, y, z=None):
        if z is None:
            z = 0
        return Vector3.CreateVector3(self.builder, x, y, z)
