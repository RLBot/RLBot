from collections import namedtuple
from typing import List

from rlbot.utils.rendering.rendering_manager import RenderingManager

Row = namedtuple('Row', 'exercise_name status_str status_color_func')

class TrainingStatusRenderer:
    """
    This class draws the current state of the training exercises
    to the game screen.
    """

    RENDER_GROUP = "TrainingStatusRenderer"
    TEXT_SCALE = 2
    LINE_HEIGHT = 40
    Y_CENTER = 300
    X_BEGIN = 10
    CONTEXT_LINES = 8  # including the "+4 exercises"

    def __init__(self, exercise_names: List[str], renderman: RenderingManager):
        self.names = exercise_names
        self.renderman = renderman
        self.rows = [ Row(name, '', renderman.black) for name in exercise_names ]
        print("rows: \n", '\n'.join(exercise_names))
        self.name_to_index = { name: i for i, name in enumerate(exercise_names) }
        self.last_modified_index = 0
        self._render()

    def update(self, row: Row):
        self.last_modified_index = self.name_to_index[row.exercise_name]
        self.rows[self.last_modified_index] = row
        self._render()

    def _render(self):
        if not self.rows:
            self.clear_screen()
            return

        self.renderman.begin_rendering(self.RENDER_GROUP)
        def get_text_y(row_y:int) -> float:
            return self.LINE_HEIGHT * row_y + self.Y_CENTER
        def draw_string(x_offset:float, row_y:int, text:str, color_func):
            self.renderman.draw_string_2d(
                self.X_BEGIN + x_offset,
                get_text_y(row_y),
                self.TEXT_SCALE,
                self.TEXT_SCALE,
                text,
                color_func()
            )

        context_begin = self.last_modified_index - self.CONTEXT_LINES # inclusive
        context_end = self.last_modified_index + self.CONTEXT_LINES # inclusive

        # If we need to summarize rows replace the first/last context row with a summary.
        if context_begin < 0:
            context_begin = 0
        elif context_begin > 0:
            context_begin += 1
            draw_string(0, -self.CONTEXT_LINES, f'...{context_begin} exercises...', self.renderman.pink)

        if context_end >= len(self.names):
            context_end = len(self.names) - 1
        elif context_end < len(self.names) - 1:
            context_end -= 1
            draw_string(0, self.CONTEXT_LINES, f'...{(len(self.rows)) - context_end} exercises...', self.renderman.grey)

        r = range(context_begin, context_end+1)
        print (''.join(
            'x' if i==self.last_modified_index else '-' if i in r else ' '
            for i in range(len(self.names))
        ))
        for context_i in r:
            row = self.rows[context_i]
            y = context_i - self.last_modified_index
            draw_string(0, y, f'[       ] {row.exercise_name}', self.renderman.white)
            draw_string(10, y, row.status_str, row.status_color_func)

        self.renderman.end_rendering()

    def clear_screen(self):
        self.renderman.clear_screen(self.RENDER_GROUP)
