import tkinter as tk
from tkinter import ttk
from configparser import RawConfigParser

from gui import match_settings_frame
from gui.team_frames.team_frame_notebook import NotebookTeamFrame
from gui.utils import get_file, IndexManager
from utils.rlbot_config_parser import create_bot_config_layout, get_num_players
from gui.agent_frames.agent_frame import AgentFrame
from gui.team_frames.base_team_frame import BaseTeamFrame


def load_cfg(team1=None, team2=None, match_settings=None, config_path=None):
    if config_path is None:
        config_path = get_file(
            filetypes=[("Config File", "*.cfg")],
            title="Choose a file")
    raw_config = RawConfigParser()
    raw_config.read(config_path)
    team_size = get_num_players(raw_config)
    overall_config = create_bot_config_layout()
    overall_config.parse_file(raw_config, team_size)
    if team1 is not None:
        team1.load_agents(overall_config)
    if team2 is not None:
        team2.load_agents(overall_config)
    if match_settings is not None:
        match_settings.load_match_settings(overall_config)
    return overall_config

def save_cfg(overall_config, team1, team2, match_settings):
    with open("rlbot2.cfg", "w") as f:
        f.write(str(overall_config))

def start_running():
    print("Need to start now")


def main():
    root = tk.Tk()
    match_settings = match_settings_frame.SettingsFrame(root)
    overall_config = load_cfg(config_path="rlbot.cfg")
    index_manager = IndexManager()

    # Create team frames
    team1 = NotebookTeamFrame(root, 0, index_manager, AgentFrame, overall_config)
    team2 = NotebookTeamFrame(root, 1, index_manager, AgentFrame, overall_config)
    team1.initialize_team_frame()
    team2.initialize_team_frame()

    # Setup grid
    match_settings.grid(row=0, column=0, columnspan=2)
    team1.grid(row=1, column=0, sticky="nsew")
    team2.grid(row=1, column=1, sticky="nsew")

    # Add buttons
    buttons_frame = ttk.Frame(root)
    ttk.Button(buttons_frame, text="Load", command=lambda: load_cfg(team1, team2, match_settings)).grid(row=0, column=0)
    ttk.Button(buttons_frame, text="Save", command=lambda: save_cfg(overall_config, team1, team2, match_settings)).grid(row=0, column=1)
    ttk.Button(buttons_frame, text="Start", command=start_running).grid(row=0, column=2)
    for i in range(3):
        buttons_frame.grid_columnconfigure(i, weight=1)
    buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

    root.mainloop()


if __name__ == '__main__':
    main()
