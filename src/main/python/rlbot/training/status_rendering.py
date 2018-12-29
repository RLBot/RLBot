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
    Y_BEGIN = 100
    X_BEGIN = 10
    PAGE_SIZE = 6  # Numer of exercise names drawn at once

    def __init__(self, exercise_names: List[str], renderman: RenderingManager):
        self.names = exercise_names
        self.renderman = renderman
        self.rows = [ Row(name, '', renderman.black) for name in exercise_names ]
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
            return self.LINE_HEIGHT * row_y + self.Y_BEGIN
        def draw_string(x_offset:float, row_y:int, text:str, color_func):
            self.renderman.draw_string_2d(
                self.X_BEGIN + x_offset,
                get_text_y(row_y),
                self.TEXT_SCALE,
                self.TEXT_SCALE,
                text,
                color_func()
            )

        if len(self.rows) > self.PAGE_SIZE:
            draw_string(0, -1, f'Progress: {self.last_modified_index+1} / {len(self.rows)}', self.renderman.grey)
        page_begin = (self.last_modified_index // self.PAGE_SIZE) * self.PAGE_SIZE
        for i in range(page_begin, min(page_begin + self.PAGE_SIZE, len(self.rows))):
            row = self.rows[i]
            y = i % self.PAGE_SIZE
            draw_string(0, y, f'[         ] {row.exercise_name}', self.renderman.white)
            draw_string(15, y, row.status_str, row.status_color_func)

        self.renderman.end_rendering()

    def clear_screen(self):
        self.renderman.clear_screen(self.RENDER_GROUP)
