using FlatBuffers;

namespace RLBotDotNet.Renderer
{
    /// <summary>
    /// Renderer that uses a name as its index.
    /// </summary>
    public class NamedRenderer : Renderer
    {
        /// <summary>
        /// Constructs a new instance of NamedRenderer using the render name as the index.
        /// </summary>
        /// <param name="renderName">The name to use as the render index.</param>
        public NamedRenderer(string renderName) : base(renderName.GetHashCode()) { }

        /// <summary>
        /// Starts the render packet.
        /// </summary>
        public void StartPacket()
        {
            Builder = new FlatBufferBuilder(1000);
        }

        /// <summary>
        /// Finishes and sends the render packet.
        /// </summary>
        public void FinishAndSend()
        {
            SendPacket(FinishPacket());
        }

        private RenderPacket FinishPacket()
        {
            return DoFinishPacket();
        }
    }
}