using System;

namespace RLBotDotNet.Utils
{
    [Serializable]
    public class FlatbuffersPacketException : Exception
    {
        public FlatbuffersPacketException() { }
        public FlatbuffersPacketException(string message) : base(message) { }
        public FlatbuffersPacketException(string message, Exception inner) : base(message, inner) { }

        protected FlatbuffersPacketException(
            System.Runtime.Serialization.SerializationInfo info,
            System.Runtime.Serialization.StreamingContext context) : base(info, context) { }
    }
}