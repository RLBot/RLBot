namespace RLBotDotNet.GameState
{
    public class GameStatePacket
    {
        public byte[] Data { get; private set; }

        public GameStatePacket(byte[] data)
        {
            Data = data;
        }
    }
}
