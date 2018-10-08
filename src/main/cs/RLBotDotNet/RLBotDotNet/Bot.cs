using rlbot.flat;
using RLBotDotNet.Utils;
using System;
using RLBotDotNet.Renderer;
using RLBotDotNet.GameState;

namespace RLBotDotNet
{
    /// <summary>
    /// Inherit from this class to make a bot.
    /// Bot logic that should be executed every frame goes in <see cref="GetOutput(GameTickPacket)"/>
    /// </summary>
    public abstract class Bot : IDisposable
    {
        private const float MAX_CHAT_RATE = 2.0f;
        private const int MAX_CHAT_COUNT = 5;

        /// <summary>
        /// The name given to the bot in its configuration file.
        /// </summary>
        public readonly string name;
        /// <summary>
        /// The team the bot is on (0 for blue, 1 for orange).
        /// </summary>
        public readonly int team;
        /// <summary>
        /// The index of the bot in the match.
        /// </summary>
        public readonly int index;

        private DateTime lastChatTime;
        private bool resetChatTime;
        private int chatCounter;
        private Renderer.Renderer _renderer;

        /// <summary>
        /// Creates a bot instance. To be used by the BotManager.
        /// </summary>
        public Bot(string botName, int botTeam, int botIndex)
        {
            name = botName;
            team = botTeam;
            index = botIndex;
        }

        /// <summary>
        /// This method should contain the bot logic that should be executed every frame.
        /// </summary>
        /// <param name="gameTickPacket">The game data input.</param>
        /// <returns>Should return the Controller outputs that the bot should execute.</returns>
        public abstract Controller GetOutput(GameTickPacket gameTickPacket);

        /// <summary>
        /// Gets the renderer.
        /// </summary>
        protected Renderer.Renderer Renderer => _renderer;

        internal void SetRenderer(Renderer.Renderer renderBuilder)
        {
            _renderer = renderBuilder;
        }

        protected FieldInfo GetFieldInfo()
        {
            try
            {
                return RLBotInterface.GetFieldInfo();
            }
            catch (FlatbuffersPacketException)
            {
                throw new FlatbuffersPacketException("The game did not send any information. " +
                    "This could mean that the match has not started yet. " +
                    "This happens when you run the bot before (or as soon as) the RLBot DLL is injected " +
                    "and the game has not started the match yet. This usually happens on the map loading screen.");
            }
        }

        protected BallPrediction GetBallPrediction()
        {
            return RLBotInterface.GetBallPredictionData();
        }

        protected RigidBodyTick GetRigidBodyTick()
        {
            return RLBotInterface.GetRigidBodyTick();
        }

        protected void SendQuickChatFromAgent(bool teamOnly, QuickChatSelection quickChat)
        {
            /*
                Passes the agents quick chats to the other bots.
                This does perform limiting.
                You are limited to 5 quick chats in a 2 second period starting from the first chat.
                This means you can spread your chats out to be even within that 2 second period.
                You could spam them in the first little bit but then will be throttled.
           */
            try
            {
                TimeSpan timeSinceLastChat = DateTime.Now - lastChatTime;
                if (!resetChatTime && timeSinceLastChat.TotalSeconds >= MAX_CHAT_RATE)
                {
                    resetChatTime = true;
                }

                if (resetChatTime)
                {
                    lastChatTime = DateTime.Now;
                    chatCounter = 0;
                    resetChatTime = false;
                }

                if (chatCounter < MAX_CHAT_COUNT)
                {
                    RLBotInterface.SendQuickChatFlat(index, teamOnly, quickChat);
                    chatCounter++;
                }
                else
                {
                    Console.WriteLine($"Quick chat disabled for {(int)(MAX_CHAT_RATE - timeSinceLastChat.TotalSeconds)} seconds.");
                }
            }
            catch (FlatbuffersPacketException)
            {
                throw new FlatbuffersPacketException("The game did not send any information. " +
                                                     "This could mean that the match has not started yet. " +
                                                     "This happens when you run the bot before (or as soon as) the RLBot DLL is injected " +
                                                     "and the game has not started the match yet. This usually happens on the map loading screen.");
            }
        }

        /// <summary>
        /// Allows the bot to set the games' state just like in training mode.
        /// </summary>
        /// <param name="gameState"></param>
        protected void SetGameState(GameState.GameState gameState)
        {
            if (gameState == null)
                throw new ArgumentNullException("gameState");

            RLBotInterface.SetGameStatePacket(gameState.BuildGameStatePacket());
        }

        /// <summary>
        /// This optional method will be called on bot shutdown and should contain code that cleans up resources used by the bot.
        /// </summary>
        public virtual void Dispose()
        {
            // Empty virtual Dispose() to preserve compatibility with previous versions of RLBot
        }
    }
}
