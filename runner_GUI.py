import tkinter as tk
from tkinter import ttk

from gui import match_settings_frame
import gui.team_frame_notebook as team_frame


def load_cfg():
    print("Need to load cfg")


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
    ttk.Button(buttons_frame, text="Load", command=load_cfg).grid(row=0, column=0)
    ttk.Button(buttons_frame, text="Save", command=save_cfg).grid(row=0, column=1)
    ttk.Button(buttons_frame, text="Start", command=start_running).grid(row=0, column=2)
    for i in range(3):
        buttons_frame.grid_columnconfigure(i, weight=1)
    buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

    root.mainloop()


if __name__ == '__main__':
    main()
