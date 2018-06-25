using rlbot.flat;
using RLBotDotNet.Utils;

namespace RLBotDotNet
{
    /// <summary>
    /// Inherit from this class to make a bot.
    /// Bot logic that should be executed every frame goes in <see cref="GetOutput(GameTickPacket)"/>
    /// </summary>
    public abstract class Bot
    {
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

        protected FieldInfo GetFieldInfo()
        {
            return RLBotInterface.GetFieldInfo();
        }
    }
}
