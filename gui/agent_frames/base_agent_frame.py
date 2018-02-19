import tkinter as tk


class BaseAgentFrame(tk.Frame):

    config_object = None  # The config that is
    overall_config = None  # The config that is shared by all agent frames.
    overall_index = -1  # The index that grabs data from the overall_config
    team_index = -1  # The index representing what team the agent belongs to.
    parent = None  # The parent frame

    def __init__(self, parent, team_index, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.team_index = team_index
        self.parent = parent

    def initialise_widgets(self):
        pass

    @staticmethod
    def grid_items(start_row=0, start_index=0, *widgets):
        """Grid all items found in WIDGETS starting in row START_ROW from index START_INDEX"""
        for row, widget_list in enumerate(widgets):
            row += start_row
            for column, widget in enumerate(widget_list):
                column += start_index
                widget.grid(row=row, column=column, sticky="nsew")

    def load_config(self, overall_config_file, overall_index):
        pass
