import flatbuffers
from RLBotMessages.flat import RenderGroup
from RLBotMessages.flat import Color
from RLBotMessages.flat import RenderMessage
from RLBotMessages.flat import Vector3
from RLBotMessages.flat import Float
from RLBotMessages.flat.RenderType import RenderType

from RLBotFramework.utils.rendering.rendering_manager import RenderingManager


class RenderingGroupManager(RenderingManager):
    builder = None
    render_list = []

    def __init__(self):
        super().__init__()
        self.ignored_funcs.append('create_vector')
        self.ignored_funcs.append('wrap_float')

    def begin_rendering(self):
        self.builder = flatbuffers.Builder(0)
        self.render_list = []
        self.render_state = True

    def end_rendering(self):
        self.render_state = False

        list_length = len(self.render_list)

        RenderGroup.RenderGroupStartRenderMessagesVector(self.builder, list_length)

        for i in reversed(range(0, list_length)):
            self.builder.PrependUOffsetTRelative(self.render_list[i])

        messages = self.builder.EndVector(list_length)

        RenderGroup.RenderGroupStart(self.builder)
        RenderGroup.RenderGroupAddRenderMessages(self.builder, messages)
        result = RenderGroup.RenderGroupEnd(self.builder)

        self.builder.Finish(result)

        buf = self.builder.Output()
        self.send_group(buf)

    def draw_line_2d(self, x1, y1, x2, y2, color):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawLine2D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.create_vector(x1, y1))
        RenderMessage.RenderMessageAddEnd(messageBuilder, self.create_vector(x2, y2))
        message = RenderMessage.RenderMessageEnd(messageBuilder)

        self.render_list.append(message)
        return self

    def draw_line_3d(self, vec1, vec2, color):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawLine2D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.create_vector(*vec1))
        RenderMessage.RenderMessageAddEnd(messageBuilder, self.create_vector(*vec2))
        message = RenderMessage.RenderMessageEnd(messageBuilder)

        self.render_list.append(message)
        return self

    def draw_line_2d_3d(self, x, y, vec, color):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawLine2D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.create_vector(x, y))
        RenderMessage.RenderMessageAddEnd(messageBuilder, self.create_vector(*vec))
        message = RenderMessage.RenderMessageEnd(messageBuilder)

        self.render_list.append(message)
        return self

    def draw_rect_2d(self, x, y, width, height, filled, color):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawRect2D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.create_vector(x, y))
        RenderMessage.RenderMessageAddScaleX(messageBuilder, width)
        RenderMessage.RenderMessageAddScaleY(messageBuilder, height)
        RenderMessage.RenderMessageAddIsFilled(messageBuilder, filled)
        message = RenderMessage.RenderMessageEnd(messageBuilder)

        self.render_list.append(message)
        return self

    def draw_rect_3d(self, vec, width, height, filled, color):
        messageBuilder = self.builder

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawRect2D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.create_vector(*vec))
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
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawRect2D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.create_vector(x, y))
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
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawRect2D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, self.create_vector(*vec))
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

    def wrap_float(self, number):
        return Float.CreateFloat(self.builder, number)

    def create_vector(self, x, y, z=None):
        if z is None:
            z = 0
        return Vector3.CreateVector3(self.builder, x, y, z)
