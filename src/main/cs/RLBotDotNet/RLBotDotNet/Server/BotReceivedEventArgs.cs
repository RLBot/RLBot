using System;

namespace RLBotDotNet.Server
{
    /// <summary>
    /// Event arguments that contain the message of the client to the server.
    /// </summary>
    public class BotReceivedEventArgs : EventArgs
    {
        string message;

        public BotReceivedEventArgs(string eventMessage)
        {
            message = eventMessage;
        }
    }
}
