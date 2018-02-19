import os
import importlib
import inspect
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename


class TeamFrame(tk.Frame):
    def __init__(self, parent, is_blue_team, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.is_blue = is_blue_team

        self.agents_frame = ttk.Notebook(self)
        self.agents_frame.bind("<<NotebookTabChanged>>", lambda event: self.switch_tab())
        self.add_agent_frame = tk.Frame(self.agents_frame)
        self.agents_frame.add(self.add_agent_frame, text="  +  ")

        self.agents = list()
        self.add_agent(0)

        self.agents_frame.pack(side="top", fill="both")

    def switch_tab(self):
        """Handle tab switch to add an agent if switched to Add Agent tab"""
        if self.agents_frame.tab(self.agents_frame.index("current"), option="text") == "  +  ":
            self.add_agent(self.agents_frame.index("current"))

    def update_tabs(self):
        color = "Blue" if self.is_blue else "Orange"
        for i, widget in reversed(list(enumerate(self.agents_frame.tabs()))):
            label = self.agents_frame.tab(widget, option="text")
            if not label.endswith(str(i + 1)) and label != "  +  ":
                self.agents_frame.tab(widget, text=color + " Bot " + str(i + 1))

    def add_agent(self, index):
        """Add an agent to the according team."""
        color = "Blue" if self.is_blue else "Orange"
        self.agents.append(self.AgentFrame(self.agents_frame, self.is_blue))
        self.agents_frame.insert(index, self.agents[index], text=color + " Bot " + str(index + 1))
        if len(self.agents) > 4:
            self.agents_frame.hide(self.add_agent_frame)
        self.agents_frame.select(index)

    def remove_agent(self, agent):
        """Remove agent AGENT from the list and Notebook"""
        self.agents_frame.hide(self.add_agent_frame)
        agent.destroy()
        self.agents.remove(agent)
        if len(self.agents) == 0:
            self.add_agent(0)
        self.agents_frame.add(self.add_agent_frame)
        self.update_tabs()

    class AgentFrame(tk.Frame):
        bot_config = None
        agent_class = None
        config_options_path = {}

        looks_widgets = None
        is_bot_widgets = None
        rlbot_controlled_widgets = None
        bot_level_widgets = None
        agent_path_widgets = None
        agent_config_widgets = None
        custom_agent_options = None

        def __init__(self, parent, is_blue_team, *args, **kwargs):
            tk.Frame.__init__(self, parent, *args, *kwargs)
            self.agent_path = tk.StringVar()
            self.looks_path = tk.StringVar()
            self.is_bot = tk.BooleanVar()
            self.rlbot_controlled = tk.BooleanVar()
            self.bot_level = tk.StringVar(value="All-Star")

            self.is_blue = is_blue_team
            self.parent = parent
            self.initialise_widgets()

        def initialise_widgets(self):
            self.looks_widgets = list()  # row 0
            self.looks_widgets.append(ttk.Label(self, text="Loadout path:", anchor="e"))
            self.looks_widgets.append(ttk.Entry(self, textvariable=self.looks_path, state="readonly", takefocus=False))
            self.looks_widgets.append(ttk.Button(self, text="Select file", command=self.change_looks_path))

            # rlbot.cfg options
            self.is_bot_widgets = list()  # row 1
            self.is_bot_widgets.append(ttk.Label(self, text="Is bot: ", anchor="e"))
            self.is_bot_widgets.append(
                ttk.Combobox(self, textvariable=self.is_bot, values=(True, False), state="readonly"))
            self.is_bot_widgets[1].bind("<<ComboboxSelected>>", lambda e: self.change_is_bot())
            self.is_bot_widgets[1].current(0)

            self.rlbot_controlled_widgets = list()  # row 2
            self.rlbot_controlled_widgets.append(ttk.Label(self, text="RLBot controlled: ", anchor="e"))
            self.rlbot_controlled_widgets.append(
                ttk.Combobox(self, textvariable=self.rlbot_controlled, values=(True, False), state="readonly"))
            self.rlbot_controlled_widgets[1].bind("<<ComboboxSelected>>", lambda e: self.change_rlbot_controlled())
            self.rlbot_controlled_widgets[1].current(1)

            self.bot_level_widgets = list()
            self.bot_level_widgets.append(ttk.Label(self, text="Bot level: ", anchor="e"))
            self.bot_level_widgets.append(ttk.Combobox(self, textvariable=self.bot_level, state="readonly",
                                                       values=("Rookie", "Pro", "All-Star")))
            # Agent path
            self.agent_path_widgets = list()  # row 4
            self.agent_path_widgets.append(ttk.Label(self, text="Agent path: ", anchor="e"))
            self.agent_path_widgets.append(
                ttk.Entry(self, textvariable=self.agent_path, state="readonly", takefocus=False))
            self.agent_path_widgets.append(
                ttk.Button(self, text="Select file", command=self.change_bot_path))

            # Agent config
            self.agent_config_widgets = list()  # row 5
            self.agent_config_widgets.append(ttk.Label(self, text="Bot Parameters: ", anchor="e"))
            self.agent_config_widgets.append(ttk.Combobox(self, state="readonly"))
            self.agent_config_widgets[1].bind("<<ComboboxSelected>>", lambda e: self.change_config())
            self.agent_config_widgets.append(
                ttk.Button(self, text="Add config", command=self.add_config_option, state="disabled"))

            self.custom_agent_options = tk.Frame(self, borderwidth=2, relief=tk.SUNKEN)  # row 7
            ttk.Button(self, text="Remove", command=lambda: self.parent.master.remove_agent(self)).grid(row=8, column=2)

            self.grid_items(0, 0, self.looks_widgets, self.is_bot_widgets)
            self.change_is_bot()
            self.change_rlbot_controlled()

        def initialise_custom_config(self):
            """Create the Custom Config Frame containing all widgets for editing the parameters."""
            for widget in self.custom_agent_options.grid_slaves():
                widget.grid_forget()
            try:
                self.bot_config = self.agent_class[1].get_parameters_header()
            except AttributeError:
                error = "This class does not contain a config method, unable to create custom config"
                ttk.Label(self.custom_agent_options, text=error).grid()
                return

            if not self.bot_config.values:
                ttk.Label(self.custom_agent_options, text="No Bot Parameters for this agent").grid()
                return

            ttk.Label(self.custom_agent_options, text="Bot Parameters", anchor="center").grid(row=0, column=0,
                                                                                              columnspan=2)
            for parameter_index, (parameter_name, parameter) in enumerate(self.bot_config.values.items()):
                ttk.Label(self.custom_agent_options, text=parameter_name + ":", anchor='e').grid(
                    row=parameter_index + 1, column=0, sticky="ew")
                big = 20000000
                if parameter.type == int:
                    parameter.value = tk.IntVar()
                    widget = tk.Spinbox(self.custom_agent_options, textvariable=parameter.value, from_=0, to=big)
                elif parameter.type == float:
                    parameter.value = tk.DoubleVar()
                    widget = tk.Spinbox(self.custom_agent_options, textvariable=parameter.value, from_=0, to=big,
                                        increment=.01)
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
            self.custom_agent_options.grid_columnconfigure(1, weight=1)

        def add_config_option(self):
            """Popup, ask for an extra config option and add it to the combobox"""
            config_path = askopenfilename(
                initialdir=os.path.dirname(os.path.realpath(__file__)),
                filetypes=[("Config File", "*.cfg")],
                title="Choose a file.")
            if config_path:
                config_name = os.path.splitext(os.path.basename(os.path.realpath(config_path)))[0]
                self.config_options_path[config_name] = config_path
                self.agent_config_widgets[1]['values'] += (config_name,)
                self.agent_config_widgets[1].set(config_name)
                self.change_config()

        def change_config(self):
            """Handle ComboboxSelected Event and show/hide the Custom Frame."""
            config_name = self.agent_config_widgets[1].get()
            if config_name == "custom":
                if not self.custom_agent_options.winfo_ismapped():
                    self.custom_agent_options.grid(row=6, column=0, columnspan=3, sticky="nsew")
            else:
                if self.custom_agent_options.winfo_ismapped():
                    self.custom_agent_options.grid_forget()

        def change_is_bot(self, hide=False):
            """Hide or show the widgets which have to do with the is_bot value."""
            if self.is_bot.get() and not hide:
                if self.rlbot_controlled_widgets[0].winfo_ismapped():
                    return
                self.grid_items(2, 0, self.rlbot_controlled_widgets)
                self.change_rlbot_controlled()
            else:
                if not self.rlbot_controlled_widgets[0].winfo_ismapped():
                    return
                for widget in self.grid_slaves(row=2):
                    widget.grid_forget()
                self.change_rlbot_controlled(hide=True)

        def change_bot_path(self):
            """Popup, ask for a new agent path and apply that path."""
            agent_file_path = askopenfilename(
                initialdir=os.path.dirname(os.path.realpath(__file__)),
                filetypes=[("Python File", "*.py")],
                title="Choose a file")
            if agent_file_path:
                self.agent_path.set(agent_file_path)
                self.agent_config_widgets[2]["state"] = "normal"
                self.agent_config_widgets[1]['values'] = ("custom",)
                self.agent_config_widgets[1].set("custom")
                module = self.agent_path.get().replace(os.path.dirname(os.path.realpath(__file__)).replace(os.sep, "/"),
                                                       "", 1).replace("/", ".")[1:-3]
                trainer_package = importlib.import_module(module)
                trainer_classes = [m for m in inspect.getmembers(trainer_package, inspect.isclass) if
                                   m[1].__module__ == module]
                if len(trainer_classes) > 1:
                    popup = tk.Toplevel()
                    popup.title("Choose agent class")
                    popup.transient(self)
                    popup.grab_set()
                    popup.protocol("WM_DELETE_WINDOW", lambda: None)
                    selected = tk.IntVar()
                    tk.Label(popup, text="Select the class and press continue").grid(row=0, column=0, columnspan=2,
                                                                                     padx=(10, 10), pady=(10, 5))
                    for i in range(len(trainer_classes)):
                        ttk.Radiobutton(popup, text=trainer_classes[i][0], value=i, variable=selected).grid(
                            row=i + 1, column=0, sticky="nsew", padx=(10, 0))
                    selected.set(0)

                    def chosen_class():
                        self.agent_class = trainer_classes[selected.get()]
                        popup.destroy()

                    ttk.Button(popup, text="Continue", command=chosen_class).grid(row=len(trainer_classes), column=1,
                                                                                  padx=(0, 10), pady=(0, 10))
                    self.wait_window(popup)
                else:
                    self.agent_class = trainer_classes[0]
                self.initialise_custom_config()
                self.change_config()

        def change_looks_path(self):
            """Popup, ask for the loadout config and apply that path."""
            config_path = askopenfilename(
                initialdir=os.path.dirname(os.path.realpath(__file__)),
                filetypes=[("Config File", "*.cfg")],
                title="Choose a file")
            if config_path:
                self.looks_path.set(config_path)

        def change_rlbot_controlled(self, hide=False):
            """Hide or show the widgets which have to do with the rlbot_controlled value."""
            if hide:
                for i in [3, 4, 5, 6]:
                    for widget in self.grid_slaves(row=i):
                        widget.grid_forget()
                return
            if self.rlbot_controlled.get():
                if self.rlbot_controlled_widgets[0].winfo_ismapped():
                    for widget in self.grid_slaves(row=3):
                        widget.grid_forget()
                self.grid_items(4, 0, self.agent_path_widgets, self.agent_config_widgets)
                self.custom_agent_options.grid(row=6, column=0, columnspan=3, sticky="nsew")
            else:
                for i in [4, 5, 6]:
                    for widget in self.grid_slaves(row=i):
                        widget.grid_forget()
                self.grid_items(3, 0, self.bot_level_widgets)

        def check_for_settings(self):
            """Return list with items missing, if nothing an empty list."""
            missing = list()
            if not self.looks_path.get():
                missing.append("Loadout Path")
            if self.rlbot_controlled.get():
                if not self.agent_path.get():
                    missing.append("Agent Path")
            return missing

        @staticmethod
        def grid_items(start_row=0, start_index=0, *widgets):
            """Grid all items found in WIDGETS starting in row START_ROW from index START_INDEX"""
            for row, widget_list in enumerate(widgets):
                row += start_row
                for column, widget in enumerate(widget_list):
                    column += start_index
                    widget.grid(row=row, column=column, sticky="nsew")


if __name__ == '__main__':
    root = tk.Tk()
    runner = TeamFrame(root, True)
    runner.pack(side="top", fill="both", expand=True)
    root.mainloop()
