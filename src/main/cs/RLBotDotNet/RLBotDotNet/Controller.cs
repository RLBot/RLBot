namespace RLBotDotNet
{
    /// <summary>
    /// A struct that represents the outputs that the bot should perform.
    /// </summary>
    public struct Controller
    {
        public float Throttle;
        public float Steer;
        public float Pitch;
        public float Yaw;
        public float Roll;
        public bool Jump;
        public bool Boost;
        public bool Handbrake;
        public bool UseItem;
    }
}