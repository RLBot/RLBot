import tkinter as tk
from tkinter import ttk

import runner
from gui import match_settings_frame
from gui.team_frames.team_frame_notebook import NotebookTeamFrame
from gui.team_frames.base_team_frame import BaseTeamFrame
from gui.agent_frames.agent_frame import AgentFrame
from gui.agent_frames.agent_frame_v2 import AgentFrameV2
from gui.utils import get_file, IndexManager
from utils.custom_config import ConfigObject
from utils.rlbot_config_parser import create_bot_config_layout


team_frame_types = {BaseTeamFrame: "default", "default": BaseTeamFrame,
                    NotebookTeamFrame: "notebook", "notebook": NotebookTeamFrame}
agent_frame_types = {AgentFrame: "default", "default": AgentFrame,
                     AgentFrameV2: "v2", "v2": AgentFrameV2}


class RunnerGUI(tk.Frame):
    overall_config = None
    team1 = None
    team2 = None

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.index_manager = IndexManager()
        self.gui_config = create_gui_config()
        self.gui_config.parse_file("runner_GUI_settings.cfg")

        self.latest_save_path = self.gui_config.get("GUI Configuration", "latest_save_path")

        self.load_cfg(self.latest_save_path)
        self.load_team_frames()
        self.match_settings = match_settings_frame.SettingsFrame(self.parent)
        
        parent.wm_protocol("WM_DELETE_WINDOW", lambda: self.quit_save_popup())

        self.match_settings.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.team1.grid(row=1, column=0, sticky="nsew")
        self.team2.grid(row=1, column=1, sticky="nsew")

        # Add buttons
        buttons_frame = ttk.Frame(self.parent)
        ttk.Button(buttons_frame, text="Load", command=lambda: self.load_cfg(teams=True, match_settings=True)).grid(
            row=0, column=0)
        ttk.Button(buttons_frame, text="Save", command=lambda: self.save_cfg(
            overall_config=self.overall_config, gui_config=self.gui_config)).grid(row=0, column=1)
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
            self.team1.load_agents(self.overall_config)
            self.team2.load_agents(self.overall_config)
        if match_settings:
            self.match_settings.load_match_settings(self.overall_config)

    def load_team_frames(self):
        layout_header = self.gui_config["GUI Configuration"]
        agent_frame = agent_frame_types.get(layout_header.get("agent_type"), AgentFrame)

        team1type = team_frame_types.get(layout_header.get("blue_team_type"), BaseTeamFrame)
        self.team1 = team1type(self.parent, 0, self.index_manager, agent_frame, self.overall_config)

        team2type = team_frame_types.get(layout_header.get("orange_team_type"), BaseTeamFrame)
        self.team2 = team2type(self.parent, 1, self.index_manager, agent_frame, self.overall_config)
        self.team1.initialize_team_frame()
        self.team2.initialize_team_frame()

    def save_cfg(self, overall_config=None, path=None, gui_config=None):
        if overall_config is not None:
            if path is None:
                path = get_file(
                    filetypes=[("Config File", "*.cfg")],
                    title="Choose a file")
            if path:
                self.gui_config.set_value("GUI Configuration", "latest_save_path", path)
                with open(path, "w") as f:
                    f.write(str(overall_config))
        if gui_config is not None:
            with open("runner_GUI_settings.cfg", "w") as f:
                f.write(str(gui_config))

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
            new_config = self.overall_config.copy()
            new_config.set_value("RLBot Configuration", "num_participants", len(self.index_manager.numbers))
            self.reclassify_indices(new_config.get_header("Participant Configuration"))
            self.save_cfg(overall_config=new_config, gui_config=self.gui_config)
            popup.destroy()

        ttk.Button(frame, text="Save", command=save).grid(row=1, column=1)
        ttk.Button(frame, text="Exit", command=popup.destroy).grid(row=1, column=0)
        frame.grid()
        self.parent.wait_window(popup)
        self.parent.destroy()

    def start_running(self):
        self.quit_save_popup()
        configs = dict(self.team1.get_configs())
        configs.update(self.team2.get_configs())
        runner.main(self.overall_config, configs)


def create_gui_config():
    config = ConfigObject()
    config.add_header_name("GUI Configuration") \
        .add_value("blue_team_type", str, default="default") \
        .add_value("orange_team_type", str, default="default") \
        .add_value("agent_type", str, default="default") \
        .add_value("latest_save_path", str, default="rlbot.cfg")
    return config


if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(0, 0)
    RunnerGUI(root).grid()
    root.mainloop()

