using System;
using System.Diagnostics;
using System.IO;
using System.Media;
using System.Reflection;
using System.Text.RegularExpressions;
using System.Windows.Forms;

namespace RLBot_Injector
{
    public partial class MainForm : Form
    {
        private enum ExitCodes
        {
            INJECTION_SUCCESSFUL,
            INJECTION_FAILED,
            MULTIPLE_ROCKET_LEAGUE_PROCESSES_FOUND,
            RLBOT_DLL_ALREADY_INJECTED,
            RLBOT_DLL_NOT_FOUND,
            MULTIPLE_RLBOT_DLL_FILES_FOUND
        }

        private string dllPath = null;
        private bool hidden = false;

        public MainForm(bool hidden)
        {
            this.hidden = hidden;
            InitializeComponent();

            if (hidden)
            {
                this.WindowState = FormWindowState.Minimized;
                this.ShowInTaskbar = false;
            }
        }

        private void showMessage(string text, string caption, MessageBoxButtons buttons, MessageBoxIcon icon)
        {
            if (hidden == false)
            {
                MessageBox.Show(text, caption, buttons, icon);
            }
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            string[] dllPaths = Directory.GetFiles(Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location), "RLBot*Core.dll");

            if (dllPaths.Length == 0)
            {
                showMessage("The RLBot Dll could not be found in the startup directory of this injector!",
                            "RLBot Dll not found",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Exclamation);

                Environment.Exit((int)ExitCodes.RLBOT_DLL_NOT_FOUND);
            }
            else if (dllPaths.Length > 1)
            {
                showMessage("Multiple RLBot Dll files have been found in the startup directory of this injector!\n" +
                            "Please make sure that only one RLBot Dll file exists in that directory.",
                            "Multiple RLBot Dll files found",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Exclamation);

                Environment.Exit((int)ExitCodes.MULTIPLE_RLBOT_DLL_FILES_FOUND);
            }

            dllPath = dllPaths[0];
            injectorTimer.Start();
        }

        private void injectorTimer_Tick(object sender, EventArgs e)
        {
            Process[] foundProcesses = Process.GetProcessesByName("RocketLeague");

            if (foundProcesses.Length == 1)
            {
                injectorTimer.Stop();
                statusLabel.Text = "Injecting...";
                statusLabel.Update();

                Process rlProcess = foundProcesses[0];

                foreach (ProcessModule module in rlProcess.Modules)
                {
                    if (Regex.IsMatch(module.ModuleName, "RLBot.*Core.dll"))
                    {
                        showMessage("The RLBot Dll has already been injected into Rocket League!\n" +
                            "Injecting it more than once is not possible.",
                            "RLBot Dll already injected",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Exclamation);

                        Environment.Exit((int)ExitCodes.RLBOT_DLL_ALREADY_INJECTED);
                    }
                }

                string error = string.Empty;

                if (Injector.Inject(rlProcess.Id, dllPath, ref error))
                {
                    statusLabel.Text = "Injection successful!";
                    statusLabel.Update();
                    (new SoundPlayer(Properties.Resources.Activated)).PlaySync();
                    Environment.Exit((int)ExitCodes.INJECTION_SUCCESSFUL);
                }
                else
                {
                    statusLabel.Text = "Injection failed!";
                    statusLabel.Update();
                    (new SoundPlayer(Properties.Resources.FailedToInjectTheDll)).Play();
                    showMessage(string.Format("Failed to inject the RLBot Dll: {0}.", error), "Injection failed", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    Environment.Exit((int)ExitCodes.INJECTION_FAILED);
                }
            }
            else if (foundProcesses.Length > 1)
            {
                injectorTimer.Stop();

                showMessage("Multiple Rocket League processes have been found!\n" +
                    "Please make sure that only one instance of Rocket League is running before starting this injector.",
                    "Multiple Rocket League instances found",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Exclamation);

                Environment.Exit((int)ExitCodes.MULTIPLE_ROCKET_LEAGUE_PROCESSES_FOUND);
            }
        }
    }
}
