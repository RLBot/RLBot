using rlbot.flat;
using RLBotDotNet.Utils;
using RLBotDotNet.Server;
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Collections.Generic;
using System.Threading;
using System.Linq;
using System.IO;

namespace RLBotDotNet
{
    class TimerResolutionInterop
    {
        [DllImport("ntdll.dll", SetLastError = true)]
        static extern int NtSetTimerResolution(int DesiredResolution, bool SetResolution, out int CurrentResolution);
        public static void SetResolution(int desiredResolution) => NtSetTimerResolution(desiredResolution, true, out _);

        [DllImport("ntdll.dll", SetLastError = true)]
        static extern int NtQueryTimerResolution(out int MinimumResolution, out int MaximumResolution, out int CurrentResolution);
        public static void Query(out int minResolution, out int maxResolution, out int currResolution) => NtQueryTimerResolution(out minResolution, out maxResolution, out currResolution);
        public static TimeSpan MinimumResolution { get { NtQueryTimerResolution(out int minRes, out _, out _); return new TimeSpan(minRes); } }
        public static TimeSpan MaximumResolution { get { NtQueryTimerResolution(out _, out int maxRes, out _); return new TimeSpan(maxRes); } }
        public static TimeSpan CurrentResolution { get { NtQueryTimerResolution(out _, out _, out int currRes); return new TimeSpan(currRes); } }
    }

    /// <summary>
    /// Manages the C# bots and runs them.
    /// </summary>
    /// <typeparam name="T">The custom bot class that should be run.</typeparam>
    public class BotManager<T> where T : Bot
    {
        private ManualResetEvent botRunEvent = new ManualResetEvent(false);
        private List<BotProcess> botProcesses = new List<BotProcess>();
        private Thread serverThread;
        
        /// <summary>
        /// Adds a bot to the <see cref="botProcesses"/> list if the index is not there already.
        /// </summary>
        /// <param name="bot"></param>
        private void RegisterBot(string name, int team, int index)
        {
            // Only add a bot if botProcesses doesn't contain the index given in the parameters.
            if (!botProcesses.Any(b => b.bot.index == index))
            {
                // Create a bot instance, run it in a separate thread, and add it to botProcesses.
                T bot = (T)Activator.CreateInstance(typeof(T), name, team, index);
                Thread thread = new Thread(() => RunBot(bot));
                thread.Start();

                BotProcess botProcess = new BotProcess()
                {
                    bot = bot,
                    thread = thread
                };

                botProcesses.Add(botProcess);
                Console.WriteLine("Registered bot: name={0}, team={1}, index={2}", name, team, index);
            }
        }

        /// <summary>
        /// Calls the given bot's <see cref="Bot.GetOutput(GameTickPacket)"/> method and
        /// updates its input through the interface DLL.
        /// </summary>
        /// <param name="bot"></param>
        private void RunBot(Bot bot)
        {
            while (true)
            {
                GameTickPacket gameTickPacket = RLBotInterface.GetGameTickPacket();
                Controller botInput = bot.GetOutput(gameTickPacket);
                RLBotInterface.SetBotInput(botInput, bot.index);
                botRunEvent.WaitOne();
            }
        }

        /// <summary>
        /// The main bot manager loop. This will continuously run the bots by setting <see cref="botRunEvent"/>.
        /// </summary>
        private void MainBotLoop()
        {
            TimeSpan timerResolution = TimerResolutionInterop.CurrentResolution;
            TimeSpan targetSleepTime = new TimeSpan(166667); // 16.6667 ms, or 60 FPS

            Stopwatch stopwatch = new Stopwatch();
            while (true)
            {
                try
                {
                    stopwatch.Restart();
                    botRunEvent.Set();
                    botRunEvent.Reset();

                    Thread.Sleep(targetSleepTime - stopwatch.Elapsed - timerResolution);
                    while (stopwatch.Elapsed < targetSleepTime);
                }
                catch (Exception e)
                {
                    Console.WriteLine(e.Message);
                }
            }
        }

        /// <summary>
        /// Stops the given bot's thread.
        /// </summary>
        /// <param name="botProcess">The bot process to stop.</param>
        private void StopBotProcess(BotProcess botProcess)
        {
            botProcess.thread.Abort();
            Console.WriteLine("Stopped bot: name={0}, team={1}, index={2}",
                botProcess.bot.name, botProcess.bot.team, botProcess.bot.index);
        }

        /// <summary>
        /// Start the server and be ready to manage the bots.
        /// </summary>
        /// <param name="port">The port that the manager listens to for the Python clients.</param>
        public void Start(int port)
        {
            BotManagerServer server = new BotManagerServer();
            server.BotReceivedEvent += OnBotReceived;
            serverThread = new Thread(() => server.Start(port));
            serverThread.Start();

            // Don't start main loop until botProcesses has at least 1 bot
            while (botProcesses.Count == 0)
                Thread.Sleep(16);

            // Ensure best available resolution before starting the main loop to reduce CPU usage
            TimerResolutionInterop.Query(out int minRes, out _, out int currRes);
            if (currRes > minRes) TimerResolutionInterop.SetResolution(minRes);

            MainBotLoop();
        }

        /// <summary>
        /// Method that is subscribed to <see cref="BotManagerServer.BotReceivedEvent"/>.
        /// This method parses the event's message and calls the appropriate methods.
        /// </summary>
        /// <param name="message">The message from the event.</param>
        private void OnBotReceived(string message)
        {
            try
            {
                string[] split = message.Split(new char[] { ' ' }, 5);

                if (split.Length < 2)
                    throw new Exception("Server received too few command arguments from client");

                if (split[0] == "add")
                {
                    PlaceInterfaceDlls(split[4]);
                    RegisterBot(split[1], int.Parse(split[2]), int.Parse(split[3]));
                }
                else if (split[0] == "remove")
                {
                    int index = int.Parse(split[1]);
                    BotProcess proc = botProcesses.Find(b => b.bot.index == index);

                    // Only call the bot stopping/removing methods if proc references an object and not a default value.
                    // Referencing a default value happens when Linq's Find method can't find any matches.
                    if (!proc.Equals(default(BotProcess)))
                    {
                        StopBotProcess(proc);
                        botProcesses.Remove(proc);
                    }
                }
                else
                    throw new Exception("Server received bad command from client: " + split[0]);
            }
            catch (Exception e)
            {
                Console.WriteLine(e.GetType());
                Console.WriteLine(e.Message);
                Console.WriteLine(e.StackTrace);
            }
        }

        /// <summary>
        /// Places the interface DLLs from the given directory into
        /// </summary>
        /// <param name="dllDirectory"></param>
        private void PlaceInterfaceDlls(string dllDirectory)
        {
            if (Directory.Exists(dllDirectory))
            {
                string dllName = RLBotInterface.InterfaceDllPath.Split('/')[1];
                Directory.CreateDirectory("dll");
                try
                {
                    File.Copy(Path.Combine(dllDirectory, dllName), RLBotInterface.InterfaceDllPath, true);
                }
                catch (IOException)
                {
                    // DLL is being used, therefore don't copy.
                }
            }
        }
    }
}
