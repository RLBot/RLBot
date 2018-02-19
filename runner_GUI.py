import tkinter as tk
from tkinter import ttk

from gui import match_settings_frame
import gui.team_frame_notebook as team_frame
from gui.utils import get_file


def create_load_cfg(team1, team2, match_settings):
    def load_config():
        config_file = get_file(
            filetypes=[("Config File", "*.cfg")],
            title="Choose a file")
        config_file = None
        team1.load_agents(config_file)
        team2.load_agents(config_file)
        match_settings.load_match_settings(config_file)
    return load_config

def load_cfg():
    print("Need to load cfg")


def create_save_cfg(team1, team2, match_settings):
    return save_cfg

def save_cfg():
    print("Need to save cfg")

def start_running():
    print("Need to start now")


def main():
    root = tk.Tk()
    match_settings = match_settings_frame.SettingsFrame(root)
    team1 = team_frame.TeamFrame(root, True)
    team2 = team_frame.TeamFrame(root, False)
    match_settings.grid(row=0, column=0, columnspan=2)
    team1.grid(row=1, column=0)
    team2.grid(row=1, column=1)
    buttons_frame = ttk.Frame(root)
    ttk.Button(buttons_frame, text="Load", command=create_load_cfg(team1, team2, match_settings)).grid(row=0, column=0)
    ttk.Button(buttons_frame, text="Save", command=create_save_cfg(team1, team2, match_settings)).grid(row=0, column=1)
    ttk.Button(buttons_frame, text="Start", command=start_running).grid(row=0, column=2)
    for i in range(3):
        buttons_frame.grid_columnconfigure(i, weight=1)
    buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

    root.mainloop()


if __name__ == '__main__':
    main()
