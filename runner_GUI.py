import tkinter as tk
from tkinter import ttk


from RLBotFramework.gui import match_settings_frame
from RLBotFramework.gui.team_frames.team_frame_notebook import NotebookTeamFrame
from RLBotFramework.gui.team_frames.base_team_frame import BaseTeamFrame
from RLBotFramework.gui.agent_frames.agent_frame import AgentFrame
from RLBotFramework.gui.utils import get_file, IndexManager
from RLBotFramework.setup_manager import SetupManager
from RLBotFramework.utils.custom_config import ConfigObject
from RLBotFramework.utils.rlbot_config_parser import create_bot_config_layout

team_frame_types = {BaseTeamFrame: "default", "default": BaseTeamFrame,
                    NotebookTeamFrame: "notebook", "notebook": NotebookTeamFrame}
agent_frame_types = {AgentFrame: "default", "default": AgentFrame}


class RunnerGUI(tk.Frame):
    overall_config = None
    team1 = None
    team2 = None

    def __init__(self, parent, setup_manager, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Set some values
        self.parent = parent
        self.runner = setup_manager
        self.index_manager = IndexManager(10)

        # Create GUI config layout and load it from the file
        self.gui_config = create_gui_config()
        self.gui_config.parse_file("runner_GUI_settings.cfg")

        # Load latest saved file and then initialize all agents and the match settings
        self.latest_save_path = self.gui_config.get("GUI Configuration", "latest_save_path")
        self.load_cfg(self.latest_save_path)
        self.load_team_frames()
        self.match_settings = match_settings_frame.SettingsFrame(self.parent)

        # Make sure to ask to save before quitting
        parent.wm_protocol("WM_DELETE_WINDOW", lambda: self.quit_save_popup())

        # Grid all previously created frames and the button frame
        self.match_settings.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.team1.grid(row=1, column=0, sticky="nsew")
        self.team2.grid(row=1, column=1, sticky="nsew")
        self.initialize_buttons()

    def initialize_buttons(self):
        """Creates the load, save and start buttons and grids them"""
        buttons_frame = ttk.Frame(self.parent)
        ttk.Button(buttons_frame, text="Load", command=lambda: self.load_cfg(teams=True, match_settings=True)).grid(
            row=0, column=0)
        ttk.Button(buttons_frame, text="Save", command=lambda: self.save_cfg(overall_config=self.overall_config)).grid(
            row=0, column=1)
        ttk.Button(buttons_frame, text="Start", command=lambda: self.start_running()).grid(
            row=0, column=2)
        for i in range(3):
            buttons_frame.grid_columnconfigure(i, weight=1)
        buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

    def load_cfg(self, config_path=None, teams=False, match_settings=False):
        if config_path is None:
            config_path = get_file(
                filetypes=[("Config File", "*.cfg")],
                title="Choose a file")
        if self.overall_config is None:
            self.overall_config = create_bot_config_layout()
        self.overall_config.parse_file(config_path, 10)
        if teams:
            self.index_manager.numbers = set()
            self.team1.load_agents(self.overall_config)
            self.team2.load_agents(self.overall_config)
        if match_settings:
            self.match_settings.load_match_settings(self.overall_config)

    def load_team_frames(self):
        """Load the team frames with the layout configured in the config"""
        layout_header = self.gui_config["GUI Configuration"]
        agent_frame = agent_frame_types.get(layout_header.get("agent_type"), AgentFrame)

        team1type = team_frame_types.get(layout_header.get("blue_team_type"), BaseTeamFrame)
        self.team1 = team1type(self.parent, 0, self.index_manager, agent_frame, self.overall_config)

        team2type = team_frame_types.get(layout_header.get("orange_team_type"), BaseTeamFrame)
        self.team2 = team2type(self.parent, 1, self.index_manager, agent_frame, self.overall_config)
        self.team1.initialize_team_frame()
        self.team2.initialize_team_frame()

    def save_cfg(self, overall_config=None, path=None):
        """If path not defined ask for path and then save overall_config to the path"""
        if overall_config is not None:
            if path is None:
                path = get_file(
                    filetypes=[("Config File", "*.cfg")],
                    title="Choose a file")
            if path:
                self.gui_config.set_value("GUI Configuration", "latest_save_path", path)
                with open(path, "w") as f:
                    f.write(str(overall_config))
                with open("runner_GUI_settings.cfg", "w") as f:
                    f.write(str(self.gui_config))

    def reclassify_indices(self, header):
        used_indices = sorted(self.index_manager.numbers)
        not_used_indices = [e for e in range(10) if e not in used_indices]
        order = used_indices + not_used_indices

        for name, config_value in header.values.items():
            old_values = list(config_value.value)
            for i in range(10):
                config_value.set_value(old_values[order[i]], index=i)
        return header

    def quit_save_popup(self):
        popup = tk.Toplevel()
        popup.resizable(0, 0)
        popup.grab_set()
        frame = tk.Frame(popup, borderwidth=5)
        ttk.Label(frame, text="Do you want to save before exiting the GUI?").grid(row=0, column=0, columnspan=2)

        def save():
            self.overall_config = self.overall_config.copy()
            self.overall_config.set_value("RLBot Configuration", "num_participants", len(self.index_manager.numbers))
            self.reclassify_indices(self.overall_config.get_header("Participant Configuration"))
            self.save_cfg(overall_config=self.overall_config)
            popup.destroy()

        ttk.Button(frame, text="Save", command=save).grid(row=1, column=1)
        ttk.Button(frame, text="Exit", command=popup.destroy).grid(row=1, column=0)
        frame.grid()
        self.parent.wait_window(popup)
        self.parent.destroy()

    def start_running(self):
        """
        Ask to save, grab the agent configurations
        Then make sure to reclassify to start the correct agents

        And start the match"""
        self.quit_save_popup()
        bot_configs, looks_configs = self.team1.get_configs()
        team2_configs = self.team2.get_configs()
        bot_configs.update(team2_configs[0])
        looks_configs.update(team2_configs[1])
        self.overall_config.set_value("RLBot Configuration", "num_participants", len(self.index_manager.numbers))
        self.reclassify_indices(self.overall_config["Participant Configuration"])
        self.runner.startup()
        self.runner.load_config(self.overall_config, bot_configs, looks_configs)
        self.runner.launch_bot_processes()
        self.runner.run()


def create_gui_config():
    config = ConfigObject()
    config.add_header_name("GUI Configuration") \
        .add_value("blue_team_type", str, default="default") \
        .add_value("orange_team_type", str, default="default") \
        .add_value("agent_type", str, default="default") \
        .add_value("latest_save_path", str, default="rlbot.cfg")
    return config


if __name__ == '__main__':
    runner = SetupManager()
    root = tk.Tk()
    root.resizable(0, 0)
    RunnerGUI(root, runner).grid()
    root.mainloop()

