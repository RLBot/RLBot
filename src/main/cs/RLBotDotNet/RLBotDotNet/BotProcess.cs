using System.Threading;

namespace RLBotDotNet
{
    internal struct BotProcess
    {
        Bot bot;
        Thread thread;
        int index;
    }
}
