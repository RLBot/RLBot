import tkinter as tk
from tkinter import ttk
from configparser import RawConfigParser
import webbrowser

from RLBotFramework.gui.agent_frames.base_agent_frame import BaseAgentFrame
from RLBotFramework.gui.utils import get_file
from RLBotFramework.agents.base_agent import PYTHON_FILE_KEY, LOOKS_CONFIG_KEY, BOT_CONFIG_MODULE_HEADER, \
    BOT_CONFIG_LOADOUT_HEADER, BOT_CONFIG_LOADOUT_ORANGE_HEADER
from RLBotFramework.utils.class_importer import import_agent, get_base_repo_path
from RLBotFramework.parsing.rlbot_config_parser import get_bot_config_bundle, PARTICIPANT_CONFIGURATION_HEADER, \
    PARTICIPANT_BOT_KEY, PARTICIPANT_TEAM, PARTICIPANT_RLBOT_KEY, PARTICIPANT_BOT_SKILL_KEY


class AgentFrame(BaseAgentFrame):
    name_widgets = None
    player_type_widgets = None
    bot_level_widgets = None
    rlbot_config_button = None
    agent_path_widgets = []

    def __init__(self, parent, team_index, *args, **kwargs):
        super().__init__(parent, team_index, *args, **kwargs)
        self.config(borderwidth=5)
        self.in_game_name = tk.StringVar()
        self.is_bot = tk.BooleanVar()
        self.rlbot_controlled = tk.BooleanVar()
        self.bot_level = tk.DoubleVar(value=1)
        self.player_type = tk.StringVar(value="Human")
        self.agent_path = tk.StringVar()
        self.latest_looks_path = tk.StringVar()

    def initialize_widgets(self):
        # In-game name editable
        self.name_widgets = list()
        self.name_widgets.append(ttk.Label(self, text="In-game name:", anchor="e"))
        self.name_widgets.append(ttk.Entry(self, textvariable=self.in_game_name))

        # Combobox for changing type
        self.player_type_widgets = list()
        self.player_type_widgets.append(ttk.Label(self, text="Player type: ", anchor="e"))
        self.player_type_widgets.append(ttk.Combobox(
            self, textvariable=self.player_type, values=("Human", "Psyonix Bot", "RLBot"), state="readonly"))
        self.player_type_widgets[1].bind("<<ComboboxSelected>>", lambda e: self.refresh_widgets())

        ttk.Button(self, text="Edit looks", command=self.edit_looks).grid(row=3, column=0, sticky="e")

        # Remove the agent
        ttk.Button(self, text="Remove", command=lambda: self.parent.master.remove_agent(self)).grid(row=3, column=2,
                                                                                                    sticky="e")

        # Psyonix bot level skill scale
        self.bot_level_widgets = list()
        self.bot_level_widgets.append(ttk.Label(self, text="Bot level: ", anchor="e"))
        self.bot_level_widgets.append(ttk.Scale(self, from_=0.0, to=1.0, variable=self.bot_level))

        # Configure bot popup
        self.rlbot_config_button = ttk.Button(self, text="Configure Bot", command=self.configure_rlbot)

        self.name_widgets[0].grid(row=0, column=0, sticky="nsew")
        self.name_widgets[1].grid(row=0, column=1, columnspan=2, sticky="nsew")

        self.player_type_widgets[0].grid(row=1, column=0, sticky="nsew")
        self.player_type_widgets[1].grid(row=1, column=1, columnspan=2, sticky="nsew")

        self.grid_columnconfigure(1, minsize=84)

    def refresh_widgets(self):
        for widget in self.grid_slaves(row=2):
            widget.grid_forget()
        for widget in self.grid_slaves(row=3, column=1):
            widget.grid_forget()
        if self.player_type.get() == "Human":
            self.is_bot.set(False)
            self.rlbot_controlled.set(False)
        elif self.player_type.get() == "Psyonix Bot":
            self.bot_level_widgets[0].grid(row=2, column=0, sticky="nsew")
            self.bot_level_widgets[1].grid(row=2, column=1, columnspan=2, sticky="nsew")
            self.is_bot.set(True)
            self.rlbot_controlled.set(False)
        else:
            self.rlbot_config_button.grid(row=3, column=1, sticky="e")
            self.is_bot.set(True)
            self.rlbot_controlled.set(True)

    def edit_looks(self):
        def load():
            config_file_path = get_file(
                filetypes=[("Config File", "*.cfg")],
                title="Choose a file")
            if config_file_path:
                config_parser = RawConfigParser()
                config_parser.read(config_file_path)
                self.looks_config.parse_file(config_parser)

        def save():
            config_file_path = get_file(
                filetypes=[("Config File", "*.cfg")],
                title="Choose a file")
            if config_file_path:
                self.latest_looks_path.set(config_file_path.replace(get_base_repo_path().replace("\\", "/"), '.'))
                self.write_fields_to_config()
                with open(config_file_path, "w") as f:
                    f.write(str(self.looks_config))

        window = tk.Toplevel()
        window.grab_set()

        config_frame = tk.Frame(window)
        for header_index, (header_name, header) in enumerate(self.looks_config.headers.items()):
            total_count = 0
            header_frame = tk.Frame(config_frame, borderwidth=8)
            header_frame.rowconfigure(0, minsize=25)
            if header_name == "Bot Loadout":
                header_name = "Bot Loadout Blue"
            ttk.Label(header_frame, text=header_name, anchor="center").grid(row=total_count, column=0,
                                                                            columnspan=2, sticky="new")
            total_count += 1

            self.grid_custom_options_header(header_frame, header, ["name"], 0, 0)
            header_frame.grid(row=0, column=header_index)
        config_frame.grid(row=0, column=0)

        buttons_frame = tk.Frame(window)
        ttk.Button(buttons_frame, text="Item IDs", command=lambda:
                   webbrowser.open("https://github.com/RLBot/RLBot/wiki/Item-ID's")).grid(row=0, column=0)
        ttk.Button(buttons_frame, text="Load", command=load).grid(row=0, column=1)
        ttk.Button(buttons_frame, text="Save", command=save).grid(row=0, column=2)
        ttk.Button(buttons_frame, text="Quit", command=window.destroy).grid(row=0, column=3)
        buttons_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        for i in range(4):
            buttons_frame.grid_columnconfigure(i, weight=1)

        self.wait_window(window)

    def configure_rlbot(self):
        def initialize_custom_config():
            for child in options_window.winfo_children():
                child.destroy()
            self.grid_custom_options_header(options_window, self.agent_config["Bot Parameters"], [], 0, 0)

        def load_agent_class(python_file=None):
            if python_file is None:
                python_file = get_file(
                    filetypes=[("Python File", "*.py")],
                    title="Choose a file")
                if not python_file:
                    return
            self.agent_path.set(python_file)
            self.agent_class = import_agent(python_file).get_loaded_class()
            self.agent_config = self.agent_class.create_agent_configurations().parse_file(self.agent_config)
            initialize_custom_config()

        def load_file():
            config_file_path = get_file(
                filetypes=[("Config File", "*.cfg")],
                title="Choose a file")
            if config_file_path:
                config_bundle = get_bot_config_bundle(config_file_path)

                # Set the agent_class to the right module and obtain the right config structure
                python_file = config_bundle.get_absolute_path(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY)
                load_agent_class(python_file)

                self.agent_config.parse_file(config_bundle.config_obj)

                # Make sure the custom bot parameters will get updated
                initialize_custom_config()

        def save():
            self.write_fields_to_config()
            config_file_path = get_file(
                filetypes=[("Config File", "*.cfg")],
                title="Choose a file")
            if config_file_path:
                with open(config_file_path, "w") as f:
                    f.write(str(self.agent_config))

        window = tk.Toplevel()
        window.resizable(0, 0)
        window.minsize(300, 300)
        window.grab_set()
        window.update()
        options_window = tk.Frame(window, bg='blue')
        initialize_custom_config()

        ttk.Label(window, text="Agent location: ", anchor="e").grid(row=0, column=0)
        ttk.Entry(window, textvariable=self.agent_path, state="readonly").grid(row=0, column=1)
        ttk.Button(window, text="Select file", command=load_agent_class).grid(row=0, column=2)

        buttons_frame = tk.Frame(window)
        ttk.Button(buttons_frame, text="Load", command=load_file).grid(row=0, column=0)
        ttk.Button(buttons_frame, text="Save", command=save).grid(row=0, column=1)
        ttk.Button(buttons_frame, text="Quit", command=window.destroy).grid(row=0, column=2)
        buttons_frame.grid(row=2, column=0, columnspan=3)

        for i in range(3):
            buttons_frame.grid_columnconfigure(i, weight=1)

        options_window.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.wait_window(window)

    def write_fields_to_config(self):
        i = self.overall_index

        self.overall_config[PARTICIPANT_CONFIGURATION_HEADER]["participant_team"].set_value(self.team_index, i)

        self.overall_config[PARTICIPANT_CONFIGURATION_HEADER]["participant_is_bot"].set_value(self.is_bot.get(), i)
        self.overall_config[PARTICIPANT_CONFIGURATION_HEADER]["participant_is_rlbot_controlled"].set_value(self.rlbot_controlled.get(), i)
        self.overall_config[PARTICIPANT_CONFIGURATION_HEADER]["participant_bot_skill"].set_value(self.bot_level.get(), i)

        self.agent_config[BOT_CONFIG_MODULE_HEADER][PYTHON_FILE_KEY].set_value(self.agent_path.get())
        self.agent_config[BOT_CONFIG_MODULE_HEADER][LOOKS_CONFIG_KEY].set_value(self.latest_looks_path.get())

        self.looks_config[BOT_CONFIG_LOADOUT_HEADER]["name"].set_value(self.in_game_name.get())
        self.looks_config[BOT_CONFIG_LOADOUT_ORANGE_HEADER]["name"].set_value(self.in_game_name.get())

    def load_fields_from_config(self):
        i = self.overall_index

        self.team_index = self.overall_config.getint(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TEAM, i)

        self.is_bot.set(self.overall_config.getboolean(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_KEY, i))
        self.rlbot_controlled.set(self.overall_config.getboolean(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_RLBOT_KEY, i))
        self.bot_level.set(self.overall_config.getfloat(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY, i))

        self.agent_path.set(self.agent_config.get(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY))
        self.latest_looks_path.set(self.agent_config.get(BOT_CONFIG_MODULE_HEADER, LOOKS_CONFIG_KEY))

        self.in_game_name.set(self.looks_config.get(BOT_CONFIG_LOADOUT_HEADER, 'name'))

    def load_config(self, overall_config_file, overall_index):
        super().load_config(overall_config_file, overall_index)
        if self.is_participant_bot() and not self.is_participant_custom_bot():
            self.player_type.set('Psyonix Bot')
        elif not self.is_participant_bot() and not self.is_participant_custom_bot():
            self.player_type.set('Human')
        elif self.is_participant_bot() and self.is_participant_custom_bot():
            self.player_type.set('RLBot')

