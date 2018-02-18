import tkinter as tk
from tkinter import ttk

from agents.base_agent import BaseAgent


class CustomAgentFrame(tk.Frame):
    custom_agent_options = None
    bot_config = None

    def __init__(self, parent, agent_module, bot_config, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.agent_module = agent_module
        self.custom_agent_options = tk.Frame(self, borderwidth=2, relief=tk.SUNKEN)
        if agent_module is None:
            self.agent_module = [None, BaseAgent]
        self.bot_config = bot_config

    def initialise_custom_config(self):
        """Create the Custom Config Frame containing all widgets for editing the parameters."""
        if not self.custom_agent_options.winfo_ismapped():
            self.custom_agent_options.grid(row=40, column=0, columnspan=3, sticky="nsew")
        for widget in self.custom_agent_options.grid_slaves():
            widget.grid_forget()
        if self.bot_config is None:
            self.bot_config = self.agent_module[1].create_agent_configurations()

        if self.bot_config is None:
            ttk.Label(self.custom_agent_options, text="No Bot Parameters for this agent").grid()
            return

        ttk.Label(self.custom_agent_options, text="Bot Parameters", anchor="center").grid(row=0, column=0,
                                                                                          columnspan=2)
        total_count = 0
        for header_index, (header_name, header) in enumerate(self.bot_config.headers.items()):
            ttk.Label(self.custom_agent_options, text=header_name + ":", anchor='e').grid(
                row=total_count + 1, column=0, sticky="ew")
            ttk.Label(self.custom_agent_options, text="", anchor='e').grid(
                row=total_count + 1, column=1, sticky="ew")
            total_count += 1
            for parameter_index, (parameter_name, parameter) in enumerate(header.values.items()):
                ttk.Label(self.custom_agent_options, text=parameter_name + ":", anchor='e').grid(
                    row=total_count + 1, column=0, sticky="ew")
                big = 20000000
                if parameter.type == int:
                    parameter.value = tk.IntVar()
                    widget = tk.Spinbox(self.custom_agent_options, textvariable=parameter.value, from_=0, to=big)
                elif parameter.type == float:
                    parameter.value = tk.DoubleVar()
                    widget = tk.Spinbox(self.custom_agent_options, textvariable=parameter.value, from_=0, to=big,
                                        increment=.0001)
                elif parameter.type == bool:
                    parameter.value = tk.BooleanVar()
                    widget = ttk.Combobox(self.custom_agent_options, textvariable=parameter.value, values=(True, False),
                                          state="readonly")
                    widget.current(0) if not parameter.default else widget.current(1)
                elif parameter.type == str:
                    parameter.value = tk.StringVar()
                    widget = ttk.Entry(self.custom_agent_options, textvariable=parameter.value)
                else:
                    widget = ttk.Label("Unknown type")

                widget.grid(row=parameter_index + 1, column=1, sticky="ew")

                if parameter.default is not None and parameter.type is not bool:
                    parameter.value.set(parameter.default)
                total_count += 1
        self.custom_agent_options.grid_columnconfigure(1, weight=1)

        return self.bot_config
