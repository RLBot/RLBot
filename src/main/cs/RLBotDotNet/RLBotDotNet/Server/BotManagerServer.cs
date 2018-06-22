using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

namespace RLBotDotNet.Server
{
    /// <summary>
    /// A class used for running a server to get bot data from Python clients.
    /// <para>E.g. Will receive "add MyBot 1 3 ", which means "Add a bot called MyBot to team 1 with index 3".</para>
    /// </summary>
    public class BotManagerServer
    {
        private TcpListener listener;
        public event Action<string> BotReceivedEvent;

        /// <summary>
        /// Event that gets raised whenever a message is received from the Python client.
        /// </summary>
        protected virtual void OnBotReceived(string message)
        {
            if (message != "" || message != null)
                BotReceivedEvent?.Invoke(message);
        }

        /// <summary>
        /// Starts the server, which continously listens for clients until it is stopped.
        /// </summary>
        /// <param name="port">The port to run the server on.</param>
        public void Start(int port)
        {
            if (listener == null)
            {
                listener = new TcpListener(IPAddress.Parse("127.0.0.1"), port);
                listener.Start();

                Console.WriteLine("Listening for clients on 127.0.0.1 on port {0}...", port);

                while (true)
                {
                    TcpClient client = listener.AcceptTcpClient();
                    NetworkStream stream = client.GetStream();
                    byte[] buffer = new byte[client.ReceiveBufferSize];
                    int bytes = stream.Read(buffer, 0, client.ReceiveBufferSize);

                    string receivedString = Encoding.ASCII.GetString(buffer, 0, bytes);
                    OnBotReceived(receivedString);

                    // TODO: Do some verification to know that the data was sent correctly.
                    // E.g. Echo check

                    client.Close();
                }
            }
        }

        /// <summary>
        /// Stops the server if it is running.
        /// </summary>
        public void Stop()
        {
            if (listener != null)
            {
                listener.Stop();
                listener = null;
            }
        }
    }
}
