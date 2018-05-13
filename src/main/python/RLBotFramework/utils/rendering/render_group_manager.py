import flatbuffers
from RLBotMessages.flat import RenderGroup
from RLBotMessages.flat import Color
from RLBotMessages.flat import RenderMessage
from RLBotMessages.flat import Vector3Partial
from RLBotMessages.flat.RenderType import RenderType

from RLBotFramework.utils.rendering.rendering_manager import RenderingManager


class RenderingGroupManager(RenderingManager):
    builder = None
    render_list = []

    def begin_rendering(self):
        self.builder = flatbuffers.Builder(0)
        self.render_list = []
        self.render_state = True

    def end_rendering(self):
        self.render_state = False

        list_length = len(self.render_list)

        RenderGroup.RenderGroupStart(self.builder)
        RenderGroup.RenderGroupStartRenderOptionsVector(self.builder, list_length)

        for i in reversed(range(0, list_length)):
            self.builder.PrependUOffsetTRelative(self.render_list[i])

        options = self.builder.EndVector(list_length)

        RenderGroup.RenderGroupAddRenderOptions(self.builder, options)
        result = RenderGroup.RenderGroupEnd()

        self.builder.Finish(result)

        buf = self.builder.Output()


    def draw_line_2d(self, x1, y1, x2, y2, color):
        messageBuilder = self.builder

        vectorStart = self.create_vector(x1, y1)
        vectorEnd = self.create_vector(x1, y1)

        RenderMessage.RenderMessageStart(messageBuilder)
        RenderMessage.RenderMessageAddRenderType(messageBuilder, RenderType.DrawLine2D)
        RenderMessage.RenderMessageAddColor(messageBuilder, color)
        RenderMessage.RenderMessageAddStart(messageBuilder, vectorStart)
        RenderMessage.RenderMessageAddEnd(messageBuilder, vectorEnd)
        message = RenderMessage.RenderMessageEnd(messageBuilder)
        self.render_list.append(message)

    def draw_line_3d(self, vec1, vec2, color):
        self.game.DrawLine3D(vec1, vec2, color)

    def draw_line_2d_3d(self, x, y, vec, color):
        self.game.DrawLine2D_3D(x, y, vec, color)

    def draw_rect_2d(self, x, y, width, height, filled, color):
        self.game.DrawRect2D(x, y, width, height, filled, color)

    def draw_rect_3d(self, vec, width, height, filled, color):
        self.game.DrawRect3D(vec, width, height, filled, color)

    def draw_string_2d(self, x, y, scale_x, scale_y, color, text):
        self.game.DrawString2D(x, y, scale_x, scale_y, color, text)

    def draw_string_3d(self, vec, scale_x, scale_y, color, text):
        self.game.DrawString2D(vec, scale_x, scale_y, color, text)

    def create_color(self, alpha, red, green, blue):
        colorBuilder = self.builder
        Color.ColorStart(colorBuilder)
        Color.ColorAddA(colorBuilder, alpha)
        Color.ColorAddR(colorBuilder, red)
        Color.ColorAddG(colorBuilder, green)
        Color.ColorAddB(colorBuilder, blue)
        return Color.ColorEnd(colorBuilder)

    def create_vector(self, x, y, z=None):
        Vector3Partial.Vector3PartialStart(self.builder)
        Vector3Partial.Vector3PartialAddX(self.builder, x)
        Vector3Partial.Vector3PartialAddY(self.builder, y)
        if z is not None:
            Vector3Partial.Vector3PartialAddZ(self.builder, z)

        return Vector3Partial.Vector3PartialEnd(self.builder)
