using RLBotDotNet;
using System.IO;

namespace TestBot
{
    class Program
    {
        static void Main(string[] args)
        {
            // Read the port from port.cfg.
            const string file = "Python\\port.cfg";
            string text = File.ReadAllLines(file)[0];
            int port = int.Parse(text);

            // BotManager is a generic which takes in your bot as its T type.
            BotManager<ExampleBot> botManager = new BotManager<ExampleBot>(0);
            // Start the server on the port given in the port.cfg file.
            botManager.Start(port);
        }
    }
}
