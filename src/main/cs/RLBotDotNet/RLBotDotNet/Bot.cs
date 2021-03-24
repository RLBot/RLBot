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
        private const float MaxChatRate = 2.0f;
        private const int MaxChatCount = 5;

        [Obsolete("This field is obsolete. Use Name instead.", true)]
        public readonly string name;

        [Obsolete("This field is obsolete. Use Team instead.", true)]
        public readonly int team;

        [Obsolete("This field is obsolete. Use Index instead.", true)]
        public readonly int index;

        /// <summary>
        /// The name given to the bot in its configuration file.
        /// </summary>
        public readonly string Name;

        /// <summary>
        /// The team the bot is on (0 for blue, 1 for orange).
        /// </summary>
        public readonly int Team;

        /// <summary>
        /// The index of the bot in the match.
        /// </summary>
        public readonly int Index;

        private DateTime lastChatTime;
        private bool resetChatTime;
        private int chatCounter;
        private int lastMessageId = -1;

        /// <summary>
        /// Creates a bot instance. To be used by the BotManager.
        /// </summary>
        public Bot(string botName, int botTeam, int botIndex)
        {
            Name = botName;
            Team = botTeam;
            Index = botIndex;
        }

        /// <summary>
        /// This method should contain the bot logic that should be executed every frame.
        /// </summary>
        /// <param name="gameTickPacket">The game data input.</param>
        /// <returns>Should return the Controller outputs that the bot should execute.</returns>
        public abstract Controller GetOutput(GameTickPacket gameTickPacket);

        /// <summary>
        /// Can be used to draw onto the screen.
        /// </summary>
        public Renderer.Renderer Renderer { get; internal set; }

        /// <summary>
        /// Gets information about the game that does not change, such as boost pad and goal locations.
        /// </summary>
        /// <exception cref="FlatbuffersPacketException">Throws when the game has not started yet.</exception>
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
                                                     "This happens when you run the bot before (or as soon as) RLBot.exe gets started " +
                                                     "and the game has not started the match yet. This usually happens on the map loading screen.");
            }
        }

        /// <summary>
        /// Gets a <see cref="BallPrediction"/> object containing the simulated path of the ball for the next 6 seconds.
        /// Each slice of the prediction advances by 1/60 of a second.
        /// </summary>
        /// <example>
        /// Sample code to get ball prediction and get the initial slice:
        /// <code>
        /// BallPrediction prediction = GetBallPrediction();
        /// PredictionSlide initialSlice = prediction.Slices(0).Value;
        /// </code>
        /// </example>
        protected BallPrediction GetBallPrediction()
        {
            return RLBotInterface.GetBallPredictionData();
        }

        /// <summary>
        /// Warning: This method has been deprecated.
        /// </summary>
        [ObsoleteAttribute("The RigidBodyTick has been deprecated. " +
                           "GetOutput gives all raw physics engine values, so there is no need to use GetRigidBodyTick.")]
        protected RigidBodyTick GetRigidBodyTick()
        {
            return RLBotInterface.GetRigidBodyTick();
        }

        /// <summary>
        /// Gets the configuration (possibly from RLBot.cfg) for the current match being played.
        /// </summary>
        /// <example>
        /// Sample code to get current map:
        /// <code>
        /// MatchSettings matchSettings = GetMatchSettings();
        /// GameMap map = matchSettings.GameMap;
        /// </code>
        /// </example>
        protected MatchSettings GetMatchSettings()
        {
            return RLBotInterface.GetMatchSettingsData();
        }

        /// <summary>
        /// Passes the agent's quick chats to the other bots.
        /// </summary>
        /// <param name="teamOnly">
        /// If true, only bots on the agent's team will be able to see the quick chat.<br/>
        /// If false, the quick chat sent is global and every bot will be able to see it.
        /// </param>
        /// <param name="quickChat">The quick chat that should be sent</param>
        /// <remarks>
        /// The agent is limited to 5 quick chats in a 2 second period starting from the first chat.
        /// This means you can spread your chats out to be even within that 2 second period.
        /// You could spam them in a short duration but they will be then throttled.
        /// </remarks>
        /// <exception cref="FlatbuffersPacketException">Throws when the game has not started yet.</exception>
        /// <example>
        /// Sample code to send "What a save!" globally:
        /// <code>
        /// SendQuickChatFromAgent(false, QuickChatSelection.Compliments_WhatASave);
        /// </code>
        /// </example>
        protected void SendQuickChatFromAgent(bool teamOnly, QuickChatSelection quickChat)
        {
            try
            {
                TimeSpan timeSinceLastChat = DateTime.Now - lastChatTime;
                if (!resetChatTime && timeSinceLastChat.TotalSeconds >= MaxChatRate)
                {
                    resetChatTime = true;
                }

                if (resetChatTime)
                {
                    lastChatTime = DateTime.Now;
                    chatCounter = 0;
                    resetChatTime = false;
                }

                if (chatCounter < MaxChatCount)
                {
                    RLBotInterface.SendQuickChatFlat(Index, teamOnly, quickChat);
                    chatCounter++;
                }
                else
                {
                    Console.WriteLine(
                        $"Quick chat disabled for {(int) (MaxChatRate - timeSinceLastChat.TotalSeconds)} seconds.");
                }
            }
            catch (FlatbuffersPacketException)
            {
                throw new FlatbuffersPacketException("The game did not send any information. " +
                                                     "This could mean that the match has not started yet. " +
                                                     "This happens when you run the bot before (or as soon as) RLBot.exe gets started " +
                                                     "and the game has not started the match yet. This usually happens on the map loading screen.");
            }
        }

        /// <summary>
        /// Gets all messages that have been sent since the last call to this method.
        /// </summary>
        /// <returns>List of new messages.</returns>
        /// <example>
        /// Sample code to print all messages:
        /// <code>
        /// QuickChatMessages messages = ReceiveQuickChat();
        /// for (int i = 0; i &lt; messages.MessagesLength; i++)
        /// {
        ///     QuickChat quickChat = messages.Messages(i).Value;
        ///     Console.WriteLine($"Received {quickChat.QuickChatSelection} from player #{quickChat.PlayerIndex}");
        /// }
        /// </code>
        /// </example>
        public QuickChatMessages ReceiveQuickChat()
        {
            QuickChatMessages messages = RLBotInterface.ReceiveQuickChat(Index, Team, lastMessageId);

            if (messages.MessagesLength > 0)
                lastMessageId = messages.Messages(messages.MessagesLength - 1).Value.MessageIndex;

            return messages;
        }

        /// <summary>
        /// Allows the bot to set the game's state just like in training mode.
        /// </summary>
        /// <param name="gameState">The game state that should be set.</param>
        /// <example>
        /// Sample code to set the game state:
        /// <code>
        /// GameState gameState = new GameState();
        /// CarState carState = new CarState
        /// {
        ///     Boost = 87f,
        ///     PhysicsState = new PhysicsState(
        ///         velocity: new DesiredVector3(null, null, 500),
        ///         rotation: new DesiredRotator((float) Math.PI / 2, 0, 0),
        ///         angularVelocity: new DesiredVector3(0, 0, 0)
        ///     )
        /// };
        /// gameState.SetCarState(this.index, carState);
        /// gameState.BallState.PhysicsState.Location = new DesiredVector3(0, 0, null);
        /// gameState.GameInfoState.WorldGravityZ = 700f;
        /// gameState.GameInfoState.GameSpeed = 0.8f;
        /// SetGameState(gameState);
        /// </code>
        /// With the above code:
        /// <list type="bullet">
        ///     <item>The bot will fling itself upward with its front pointed to the ceiling.</item>
        ///     <item>The ball will warp to the middle of the field but without altering its z position.</item>
        ///     <item>The world gravity will act weakly upwards. Note: Setting gravity to 0 will reset the gravity to normal settings.</item>
        ///     <item>If you want to disable gravity, set the gravity to something very small like 0.0001.</item>
        ///     <item>The game's speed will be reduced to 80% of the normal speed.</item>
        /// </list>
        /// In the above example, the ball's X and Y locations will be set to 0, but the Z will be untouched.
        /// </example>
        /// <remarks>
        /// A <c>null</c> means that the property will not be changed.
        /// Warning: Setting gravity and game speed every frame will likely cause your game to lag!
        /// It is strongly recommended you only set them when required (e.g. only at the start of the game).
        /// </remarks>
        protected void SetGameState(GameState.GameState gameState)
        {
            if (gameState == null)
                throw new ArgumentNullException(nameof(gameState));

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