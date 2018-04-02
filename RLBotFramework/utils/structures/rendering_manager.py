import ctypes

from RLBotFramework.utils.structures.game_data_struct import Vector3


class Color(ctypes.Structure):
    _fields_ = [("b", ctypes.c_char),
                ("g", ctypes.c_char),
                ("r", ctypes.c_char),
                ("a", ctypes.c_char),]


class RenderingManager():
    game = None

    def setup_function_types(self, dll_instance):
        self.game = dll_instance

        func = self.game.DrawLine2D
        func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, Color]

        func = self.game.DrawLine3D
        func.argtypes = [Vector3, Vector3, Color]

        func = self.game.DrawLine2D_3D
        func.argtypes = [ctypes.c_int32, ctypes.c_int32, Vector3, Color]

        func = self.game.DrawRect2D
        func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_, Color]

        func = self.game.DrawRect3D
        func.argtypes = [Vector3, ctypes.c_int32, ctypes.c_int32, ctypes.c_, Color]

        func = self.game.DrawString2D
        func.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_float, ctypes.c_float, Color, ctypes.POINTER(ctypes.c_char)]

        func = self.game.DrawString3D
        func.argtypes = [Vector3, ctypes.c_float, ctypes.c_float, Color, ctypes.POINTER(ctypes.c_char)]


    def begin_rendering(self):
        self.game.BeginRendering()

    def end_rendering(self):
        self.game.EndRendering()

    def draw_line_2d(self, x1, y1, x2, y2, color):
        self.game.DrawLine2D(x1, y1, x2, y2, color)

    def draw_line_3d(self, vec1, vec2, color):
        self.game.DrawLine3D(vec1, vec2, color)

    def draw_line_2d_3d(self, x, y, vec, color):
        self.game.DrawLine2D_3D(x, y, vec, color)

    def draw_rect_2d(self, x, y, width, height,  filled, color):
        self.game.DrawRect2D(x, y, width, height, filled, color)

    def draw_rect_3d(self, vec, width, height,  filled, color):
        self.game.DrawRect3D(vec, width, height, filled, color)

    def draw_string_2d(self, x, y, scale_x, scale_y, color, text):
        self.game.DrawString2D(x, y, scale_x, scale_y, color, text)

    def draw_string_3d(self, vec, scale_x, scale_y, color, text):
        self.game.DrawString2D(vec, scale_x, scale_y, color, text)
