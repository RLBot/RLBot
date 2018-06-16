using rlbot.flat;
using RLBotDotNet.Utils;
using System;
using System.Collections.Generic;
using System.Threading;
using System.Linq;

namespace RLBotDotNet
{
    /// <summary>
    /// Manages the C# bots and runs them.
    /// </summary>
    public class BotManager
    {
        private ManualResetEvent botRunEvent = new ManualResetEvent(false);
        private List<BotProcess> botProcesses;
        private GameTickPacket currentGameTickPacket;
        private FieldInfo fieldInfo;

        /// <summary>
        /// Creates a new BotManager instance to run the bots.
        /// </summary>
        /// <param name="bot">The bot that this BotManager controls.</param>
        /// <param name="port">The port that the manager listens to for the Python clients.</param>
        public BotManager(Bot bot, int port)
        {
            throw new NotImplementedException();

            /*
             * BotManager should handle the running of the bots.
             * 
             * The server should receive data about what bot processes it controls from the Python clients.
             * E.g. "{ name = "Bot1", team = 1, index = 3 }"
             * After receiving this data, it should create instances of the bots, each on different threads.
            */
        }


        /// <summary>
        /// Adds the given bot to the <see cref="botProcesses"/> list if it's not there already.
        /// </summary>
        /// <param name="bot"></param>
        private void RegisterBot(Bot bot)
        {
            // Only run the code if botProcesses doesn't contain the Bot given in the parameters.
            if (!botProcesses.Any(b => b.bot == bot))
            {
                Thread thread = new Thread(() => RunBot(bot));

                BotProcess botProcess = new BotProcess()
                {
                    bot = bot,
                    thread = thread
                };

                botProcesses.Add(botProcess);
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
                Controller botInput = bot.GetOutput(currentGameTickPacket);
                RLBotInterface.SetBotInput(botInput, bot.index);
                botRunEvent.WaitOne();
            }
        }

        /// <summary>
        /// The main bot manager loop. This will continuously run the bots by setting <see cref="botRunEvent"/>.
        /// </summary>
        private void MainBotLoop()
        {
            //GetGameTickPacket();
            //botRunEvent.Set();
            //botRunEvent.Reset();
            throw new NotImplementedException();
        }

        /// <summary>
        /// Stops the given bot's thread.
        /// </summary>
        /// <param name="botProcess">The bot process to stop.</param>
        private void StopBotProcess(BotProcess botProcess)
        {
            botProcess.thread.Abort();
        }

        /// <summary>
        /// Start the server and be ready to manage the bots.
        /// </summary>
        public void Start()
        {
            throw new NotImplementedException();
        }

        /// <summary>
        /// Calls <see cref="RLBotInterface.GetGameTickPacket"/>, and also sets <see cref="currentGameTickPacket"/>.
        /// </summary>
        /// <returns>The current frame's GameTickPacket.</returns>
        private GameTickPacket GetGameTickPacket()
        {
            currentGameTickPacket = RLBotInterface.GetGameTickPacket();
            return currentGameTickPacket;
        }

        /// <summary>
        /// Calls <see cref="RLBotInterface.GetFieldInfo"/>, and also sets <see cref="fieldInfo"/>.
        /// </summary>
        /// <returns>The game's FieldInfo.</returns>
        private FieldInfo GetFieldInfo()
        {
            // Since FieldInfo will never change during a match, we only call RLBotInterface.GetFieldInfo once.
            if (fieldInfo.Equals(null) && RLBotInterface.IsInitialized())
                fieldInfo = RLBotInterface.GetFieldInfo();

            return fieldInfo;
        }
    }
}
