import collections
import ctypes

from RLBotFramework.utils.logging_utils import get_logger
from RLBotFramework.utils.structures.game_data_struct import Vector3


class Color(ctypes.Structure):
    _fields_ = [("b", ctypes.c_char),
                ("g", ctypes.c_char),
                ("r", ctypes.c_char),
                ("a", ctypes.c_char)]


class RenderingManager:
    game = None
    render_state = False

    def setup_function_types(self, dll_instance):
        self.game = dll_instance

        func = self.game.DrawLine2D
        func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, Color]
        func.restype = ctypes.c_int


        func = self.game.DrawLine3D
        func.argtypes = [Vector3, Vector3, Color]
        func.restype = ctypes.c_int

        func = self.game.DrawLine2D_3D
        func.argtypes = [ctypes.c_int, ctypes.c_int, Vector3, Color]
        func.restype = ctypes.c_int

        func = self.game.DrawRect2D
        func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool, Color]
        func.restype = ctypes.c_int

        func = self.game.DrawRect3D
        func.argtypes = [Vector3, ctypes.c_int, ctypes.c_int, ctypes.c_bool, Color]
        func.restype = ctypes.c_int

        func = self.game.DrawString2D
        func.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_float, ctypes.c_float, Color, ctypes.POINTER(ctypes.c_char)]
        func.restype = ctypes.c_int

        func = self.game.DrawString3D
        func.argtypes = [Vector3, ctypes.c_float, ctypes.c_float, Color, ctypes.POINTER(ctypes.c_char)]
        func.restype = ctypes.c_int

    def begin_rendering(self):
        self.render_state = True
        self.game.BeginRendering()

    def end_rendering(self):
        if self.render_state:
            self.game.EndRendering()
        self.render_state = False

    def is_rendering(self):
        return self.render_state

    def draw_line_2d(self, x1, y1, x2, y2, color):
        if color is None:
            raise ValueError('wtf color is not valid')
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

    def create_color(self, alpha, red, green, blue):
        color = Color()
        color.a = alpha
        color.r = red
        color.g = green
        color.b = blue
        return color

    def black(self):
        color = Color()
        color.a = 255
        color.r = 0
        color.g = 0
        color.b = 0
        return color

    def get_render_functions(self):
        """
        Gets all the raw render functions but without giving access to any internal logic or the dll
        :return: An object with the same interface as the functions above
        """

        functions = [func for func in dir(self) if not func.startswith('__')]

        function_names = []
        filtered_functions = []

        for name in functions:  # iterate through every module's attributes
            val = getattr(self, name)
            if callable(val) and name != 'setup_function_types' and name != 'get_render_functions':
                temp_func = self.create_dynamic_function(val, self.is_rendering, self.end_rendering)
                function_names.append(name)
                filtered_functions.append(temp_func)

        FakeRenderingManager = collections.namedtuple('FakeRenderingManager', function_names)
        obj = FakeRenderingManager(*filtered_functions)

        return obj

    def create_dynamic_function(self, bounded_function, is_rendering, end_rendering):
        def temp_function(*args):
            try:
                return bounded_function(*args)
            except OSError as error:
                get_logger("Renderer").error('rendering error', str(error))
                if is_rendering() and bounded_function is not end_rendering:
                    end_rendering()

        return temp_function
