using rlbot.flat;
using RLBotDotNet.Utils;
using RLBotDotNet.Server;
using System;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Collections.Generic;
using System.Threading;
using System.Linq;
using System.IO;
using RLBotDotNet.Manager;
using RLBotDotNet.Renderer;

namespace RLBotDotNet
{
    /// <summary>
    /// Manages the C# bots and runs them.
    /// </summary>
    /// <typeparam name="T">The custom bot class that should be run.</typeparam>
    public class BotManager<T> where T : Bot
    {
        private readonly ConcurrentDictionary<int, BotLoopRenderer> _renderers;
        private List<BotProcess> botProcesses = new List<BotProcess>();
        private Thread serverThread;

        private readonly int frequency;

        /// <summary>
        /// Constructs a new instance of BotManager.
        /// </summary>
        public BotManager() : this(60) { }

        /// <summary>
        /// Constructs a new instance of BotManager.
        /// </summary>
        /// <param name="frequency">The frequency that the bot updates at: [1, 120]. Set to 0 to update at each new packet.</param>
        public BotManager(int frequency)
        {
            _renderers = new ConcurrentDictionary<int, BotLoopRenderer>();

            if (frequency > 120 || frequency < 0)
                throw new ArgumentOutOfRangeException(nameof(frequency));

            this.frequency = frequency;
        }

        /// <summary>
        /// Adds a bot to the <see cref="botProcesses"/> list if the index is not there already.
        /// </summary>
        private void RegisterBot(string name, int team, int index)
        {
            // Only add a bot if botProcesses doesn't contain the index given in the parameters.
            if (botProcesses.Any(b => b.bot.Index == index))
                return;

            AutoResetEvent botRunEvent = new AutoResetEvent(false);

            // Create a bot instance, run it in a separate thread, and add it to botProcesses.
            T bot = (T) Activator.CreateInstance(typeof(T), name, team, index);
            Thread thread = new Thread(() => RunBot(bot, botRunEvent));
            thread.Start();

            BotProcess botProcess = new BotProcess()
            {
                bot = bot,
                thread = thread,
                botRunEvent = botRunEvent
            };

            botProcesses.Add(botProcess);
            Console.WriteLine($"Registered bot: name={name}, team={team}, index={index}");
        }

        /// <summary>
        /// Calls the given bot's <see cref="Bot.GetOutput(GameTickPacket)"/> method and
        /// updates its input through the interface DLL.
        /// </summary>
        private void RunBot(Bot bot, AutoResetEvent botRunEvent)
        {
            BotLoopRenderer renderer = GetRendererForBot(bot);
            bot.Renderer = renderer;

            Console.WriteLine("Waiting for the RLBot Interface to initialize...");

            while (!RLBotInterface.IsInitialized())
                Thread.Sleep(100);

            Console.WriteLine("The RLBot Interface has been successfully initialized!");
            Console.WriteLine("Running the bot loop...");

            while (true)
            {
                try
                {
                    renderer.StartPacket();
                    GameTickPacket gameTickPacket = RLBotInterface.GetGameTickPacket();
                    Controller botInput = bot.GetOutput(gameTickPacket);
                    RLBotInterface.SetBotInput(botInput, bot.Index);
                    renderer.FinishAndSendIfDifferent();
                }
                catch (FlatbuffersPacketException)
                {
                    // Ignore if the packet size is too small. No need to warn the user.
                }
                catch (Exception e)
                {
                    // Don't crash the bot and give the user the details of the exception instead.
                    Console.WriteLine(e.GetType());
                    Console.WriteLine(e.Message);
                    Console.WriteLine(e.StackTrace);
                }

                botRunEvent.WaitOne();
            }
        }

        /// <summary>
        /// The main bot manager loop. This will continuously run the bots by setting <see cref="BotProcess.botRunEvent"/>.
        /// </summary>
        private void MainBotLoop()
        {
            if (frequency > 0)
            {
                // Retrieve packets at a fixed frequency.

                TimeSpan timerResolution = TimerResolutionInterop.CurrentResolution;
                TimeSpan targetSleepTime = new TimeSpan(10000000 / frequency);

                Stopwatch stopwatch = new Stopwatch();
                while (true)
                {
                    // Start the timer
                    stopwatch.Restart();

                    // Set off events that end up running the bot code later down the line
                    foreach (BotProcess proc in botProcesses)
                    {
                        proc.botRunEvent.Set();
                    }

                    // Sleep efficiently (but inaccurately) for as long as we can
                    TimeSpan maxInaccurateSleepTime = targetSleepTime - stopwatch.Elapsed - timerResolution;
                    if (maxInaccurateSleepTime > TimeSpan.Zero)
                        Thread.Sleep(maxInaccurateSleepTime);

                    // We can sleep the rest of the time accurately with the use of a spin-wait, this will drastically reduce the amount of duplicate packets when running at higher frequencies.
                    while (stopwatch.Elapsed < targetSleepTime) ;
                }
            }
            else
            {
                // Dynamically retrieve new packets.
                while (true)
                {
                    RLBotInterface.WaitForFreshPacket(100, 0);

                    foreach (BotProcess proc in botProcesses)
                    {
                        proc.botRunEvent.Set();
                    }
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
            Bot bot = botProcess.bot;
            try
            {
                bot.Dispose();
                botProcess.botRunEvent.Dispose();
            }
            catch (Exception e)
            {
                // Don't crash the bot and give the user the details of the exception instead.
                Console.WriteLine("Bot threw an exception during termination.");
                Console.WriteLine(e.GetType());
                Console.WriteLine(e.Message);
                Console.WriteLine(e.StackTrace);
            }

            Console.WriteLine($"Stopped bot: Name={bot.Name}, Team={bot.Team}, Index={bot.Index}");
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
                string[] split = message.Split(new char[] {'\n'}, 5);

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
                    BotProcess proc = botProcesses.Find(b => b.bot.Index == index);

                    // Only call the bot stopping/removing methods if proc references an object and not a default value.
                    // Referencing a default value happens when LINQ's Find method can't find any matches.
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
        /// Places the interface DLLs from the given directory into the bot's own DLL directory.
        /// </summary>
        /// <param name="dllDirectory">The directory to get the DLLs from</param>
        private void PlaceInterfaceDlls(string dllDirectory)
        {
            if (Directory.Exists(dllDirectory))
            {
                // The folder containing the bot runner executable MUST contain a dll folder containing an interface DLL.
                // There is a 32 bit version and a 64 bit version of the interface DLL.
                // We want to use the right one depending on the bitness we are running on.
                string dllName;
                if (Environment.Is64BitProcess)
                    dllName = "RLBot_Core_Interface.dll";
                else
                    dllName = "RLBot_Core_Interface_32.dll";

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

        private BotLoopRenderer GetRendererForBot(Bot bot)
        {
            return _renderers.GetOrAdd(bot.Index, new BotLoopRenderer(bot.Index));
        }
    }
}