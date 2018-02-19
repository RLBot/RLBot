import tkinter as tk


class AgentFrame(tk.Frame):
    def __init__(self, parent, is_blue_team, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.initialise_widgets()

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

    def load_config(self, config_file, overall_index):
        pass
