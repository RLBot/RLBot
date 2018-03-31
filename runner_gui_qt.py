from gui.qt_root import Analyser


Analyser.main(Signal.base_config)


if __name__ == '__main__':
    runner = SetupManager()
    root = tk.Tk()
    root.resizable(0, 0)
    RunnerGUI(root, runner).grid()
    root.mainloop()