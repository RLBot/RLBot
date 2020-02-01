using System;
using System.Runtime.Serialization;

namespace RLBotDotNet.Utils
{
    [Serializable]
    public class RLBotCoreException : Exception
    {
        public RLBotCoreException() { }
        public RLBotCoreException(string message) : base(message) { }
        public RLBotCoreException(string message, Exception inner) : base(message, inner) { }
        protected RLBotCoreException(SerializationInfo info, StreamingContext context) : base(info, context) { }
    }
}