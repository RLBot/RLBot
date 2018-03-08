using System;
using Grpc.Core;
using Rlbot.Api;

namespace RLBotSharp
{
    public class GrpcTest
    {
        public static void Main(string[] args)
        {
            var channel = new Channel("127.0.0.1:50051", ChannelCredentials.Insecure);

            var client = new Bot.BotClient(channel);

            var packet = new GameTickPacket();
            packet.Ball.Location.X = 1.0f;
            // TODO: build the packet
            
            var reply = client.GetControllerState(packet, deadline: DateTime.Now.AddSeconds(1));
            Console.WriteLine("Response: " + reply);
    

            channel.ShutdownAsync().Wait();
            
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
        }
        
    }
}
