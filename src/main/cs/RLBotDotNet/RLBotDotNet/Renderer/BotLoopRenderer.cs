using FlatBuffers;

namespace RLBotDotNet.Renderer
{
    /// <summary>
    /// Renderer for the bot loop.
    /// </summary>
    public class BotLoopRenderer : Renderer
    {
        private RenderPacket _previousPacket;

        internal BotLoopRenderer(int index) : base(index)
        {
        }

        /// <summary>
        /// Starts the render packet.
        /// </summary>
        public void StartPacket()
        {
            Builder = new FlatBufferBuilder(1000);
        }

        /// <summary>
        /// Finishes the render packet and sends it if it's different from the last packet.
        /// </summary>
        public void FinishAndSendIfDifferent()
        {
            var packet = DoFinishPacket();
            if (!packet.Equals(_previousPacket))
            {
                SendPacket(packet);
                _previousPacket = packet;
            }
        }
    }
}