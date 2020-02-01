using System;

namespace RLBotDotNet.Utils
{
    /// <summary>
    /// This is the ByteBuffer struct used in the interface DLL.
    /// </summary>
    public struct ByteBufferStruct
    {
        public IntPtr ptr;
        public int size;
    }
}