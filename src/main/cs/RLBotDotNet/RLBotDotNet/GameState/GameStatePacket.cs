namespace RLBotDotNet.GameState
{
    public class GameStatePacket
    {
        public byte[] Data { get; }

        public GameStatePacket(byte[] data)
        {
            Data = data;
        }
    }
}