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

        string dllPath = null;

        public MainForm()
        {
            InitializeComponent();
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            string[] dllPaths = Directory.GetFiles(Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location), "RLBot*.dll");

            if (dllPaths.Length == 0)
            {
                MessageBox.Show("The RLBot Dll could not be found in the startup directory of this injector!",
                            "RLBot Dll not found",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Exclamation);

                Environment.Exit((int)ExitCodes.RLBOT_DLL_NOT_FOUND);
            }
            else if (dllPaths.Length > 1)
            {
                MessageBox.Show("Multiple RLBot Dll files have been found in the startup directory of this injector!\n" +
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
                    if (Regex.IsMatch(module.ModuleName, "RLBot.*.dll"))
                    {
                        MessageBox.Show("The RLBot Dll has already been injected into Rocket League!\n" +
                            "Injecting it more than once is not possible.",
                            "RLBot Dll already injected",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Exclamation);

                        Environment.Exit((int)ExitCodes.RLBOT_DLL_ALREADY_INJECTED);
                    }
                }

                if (Injector.Inject(rlProcess.Id, dllPath))
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
                    (new SoundPlayer(Properties.Resources.FailedToInjectTheDll)).PlaySync();
                    Environment.Exit((int)ExitCodes.INJECTION_FAILED);
                }
            }
            else if (foundProcesses.Length > 1)
            {
                injectorTimer.Stop();

                MessageBox.Show("Multiple Rocket League processes have been found!\n" +
                    "Please make sure that only one instance of Rocket League is running before starting this injector.",
                    "Multiple Rocket League instances found",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Exclamation);

                Environment.Exit((int)ExitCodes.MULTIPLE_ROCKET_LEAGUE_PROCESSES_FOUND);
            }
        }
    }
}
