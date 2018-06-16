using rlbot.flat;
using RLBotDotNet.Utils;
using System;
using System.Collections.Generic;

namespace RLBotDotNet
{
    /// <summary>
    /// Manages the C# bots and runs them.
    /// </summary>
    public class BotManager
    {
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
             * Planned to support more than a single bot instance per BotManager,
             * so some further architecture planning is required.
             * 
             * 
             * The server should receive data about what bot processes it controls from the Python clients.
             * E.g. "{ name = "Bot1", team = 1, index = 3 }"
             * After receiving this data, it should create instances of the bots, each on different threads.
             * 
             * There should be a BotProcess struct that contains this information.
             * There should be a List that contains all the different BotProcesses.
            */
        }


        private void RunBot(Bot bot)
        {
            
        }

        private void MainBotLoop()
        {

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
