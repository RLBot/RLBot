import tkinter as tk
from tkinter import ttk
from configparser import RawConfigParser

import runner
from gui import match_settings_frame
from gui.team_frames.team_frame_notebook import NotebookTeamFrame
from gui.team_frames.base_team_frame import BaseTeamFrame
from gui.agent_frames.agent_frame import AgentFrame
from gui.utils import get_file, IndexManager
from utils.custom_config import ConfigObject
from utils.rlbot_config_parser import create_bot_config_layout, get_num_players


team_frame_types = {BaseTeamFrame: "default", "default": BaseTeamFrame,
                    NotebookTeamFrame: "notebook", "notebook": NotebookTeamFrame}
agent_frame_types = {AgentFrame: "default", "default": AgentFrame}


def load_cfg(team1=None, team2=None, match_settings=None, config_path=None):
    if config_path is None:
        config_path = get_file(
            filetypes=[("Config File", "*.cfg")],
            title="Choose a file")
    raw_config = RawConfigParser()
    raw_config.read(config_path)
    overall_config = create_bot_config_layout()
    overall_config.parse_file(raw_config, 10)
    if team1 is not None:
        team1.load_agents(overall_config)
    if team2 is not None:
        team2.load_agents(overall_config)
    if match_settings is not None:
        match_settings.load_match_settings(overall_config)
    return overall_config


def save_cfg(overall_config, path, gui_config):
    with open(path, "w") as f:
        f.write(str(overall_config))

    with open("runner_GUI_settings.cfg", "w") as f:
        f.write(str(gui_config))


def load_team_frames(root, overall_config, index_manager):
    gui_config = create_gui_config()
    gui_config.parse_file("runner_GUI_settings.cfg")
    layout_header = gui_config["Layout Configuration"]
    agent_frame = agent_frame_types.get(layout_header.get("agent_type"), AgentFrame)

    team1type = team_frame_types.get(layout_header.get("blue_team_type"), BaseTeamFrame)
    team1 = team1type(root, 0, index_manager, agent_frame, overall_config)

    team2type = team_frame_types.get(layout_header.get("orange_team_type"), BaseTeamFrame)
    team2 = team2type(root, 1, index_manager, agent_frame, overall_config)
    team1.initialize_team_frame()
    team2.initialize_team_frame()
    return team1, team2, gui_config


def create_gui_config():
    config = ConfigObject()
    config.add_header_name("Layout Configuration") \
        .add_value("blue_team_type", str, default="default") \
        .add_value("orange_team_type", str, default="default") \
        .add_value("agent_type", str, default="default")
    return config


def start_running(overall_config, team1, team2):
    configs = team1.get_configs() + team2.get_configs()
    runner.main(overall_config, configs)


def main():
    root = tk.Tk()
    root.resizable(0, 1)
    index_manager = IndexManager()
    overall_config = load_cfg(config_path="runner_GUI_settings.cfg")

    team1, team2, gui_config = load_team_frames(root, overall_config, index_manager)
    match_settings = match_settings_frame.SettingsFrame(root)

    match_settings.grid(row=0, column=0, columnspan=2, sticky="nsew")
    team1.grid(row=1, column=0, sticky="nsew")
    team2.grid(row=1, column=1, sticky="nsew")

    # Add buttons
    buttons_frame = ttk.Frame(root)
    ttk.Button(buttons_frame, text="Load", command=lambda: load_cfg(team1, team2, match_settings)).grid(row=0, column=0)
    ttk.Button(buttons_frame, text="Save", command=lambda: save_cfg(overall_config, "rlbot2.cfg", gui_config)).grid(row=0, column=1)
    ttk.Button(buttons_frame, text="Start", command=lambda: start_running(overall_config, team1, team2)).grid(row=0, column=2)
    for i in range(3):
        buttons_frame.grid_columnconfigure(i, weight=1)
    buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

    root.mainloop()


if __name__ == '__main__':
    main()
