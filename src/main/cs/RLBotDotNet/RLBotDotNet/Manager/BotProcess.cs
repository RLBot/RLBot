using System.Threading;

namespace RLBotDotNet.Manager
{
    internal struct BotProcess
    {
        public Bot bot;
        public Thread thread;
        public AutoResetEvent botRunEvent;
    }
}