import tkinter as tk
from tkinter import ttk

from RLBotFramework.agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER


class CustomAgentFrame(tk.Frame):
    custom_agent_options = None
    bot_config = None

    def __init__(self, parent, agent_module, bot_config, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.agent_module = agent_module
        self.custom_agent_options = self
        if agent_module is None:
            self.agent_module = BaseAgent
        self.bot_config = bot_config

    def initialise_custom_config(self):
        """Create the Custom Config Frame containing all widgets for editing the parameters."""
        for widget in self.grid_slaves():
            widget.grid_forget()
        if self.bot_config is None:
            self.bot_config = self.agent_module.create_agent_configurations()

        if self.bot_config is None:
            ttk.Label(self, text="No Bot Parameters for this agent").grid()
            return

        ttk.Label(self, text="Bot Parameters", anchor="center").grid(row=0, column=0,
                                                                                          columnspan=2)
        total_count = 0
        max_per_column = 12
        column_mult = 0
        for header_index, (header_name, header) in enumerate(self.bot_config.headers.items()):
            if header_name == BOT_CONFIG_MODULE_HEADER:
                continue
            if total_count > max_per_column:
                column_mult += 2
                total_count = 0
            ttk.Label(self, text=header_name + ":", anchor='e').grid(
                row=total_count + 1, column=0 + column_mult, sticky="ew")
            ttk.Label(self, text="", anchor='e').grid(
                row=total_count + 1, column=1 + column_mult, sticky="ew")
            total_count += 1
            for parameter_index, (parameter_name, parameter) in enumerate(header.values.items()):
                print(header_name, parameter_name, total_count)
                ttk.Label(self, text=parameter_name + ":", anchor='e').grid(
                    row=total_count + 1, column=0 + column_mult, sticky="ew")
                big = 20000000
                if parameter.type == int:
                    parameter.value = tk.IntVar()
                    widget = tk.Spinbox(self, textvariable=parameter.value, from_=0, to=big)
                elif parameter.type == float:
                    parameter.value = tk.DoubleVar()
                    widget = tk.Spinbox(self, textvariable=parameter.value, from_=0, to=big,
                                        increment=.0001)
                elif parameter.type == bool:
                    parameter.value = tk.BooleanVar()
                    widget = ttk.Combobox(self, textvariable=parameter.value, values=(True, False),
                                          state="readonly")
                    widget.current(0) if not parameter.default else widget.current(1)
                elif parameter.type == str:
                    parameter.value = tk.StringVar()
                    widget = ttk.Entry(self, textvariable=parameter.value)
                else:
                    widget = ttk.Label("Unknown type")

                widget.grid(row=total_count + 1, column=1 + column_mult, sticky="ew")

                if parameter.default is not None and parameter.type is not bool:
                    parameter.value.set(parameter.default)
                total_count += 1
        self.grid_columnconfigure(1, weight=1)

        return self.bot_config
