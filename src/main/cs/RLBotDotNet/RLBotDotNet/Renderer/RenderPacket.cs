using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;

namespace RLBotDotNet.Renderer
{
    /// <summary>
    /// Packet for render messages that get sent through the RLBot interface.
    /// </summary>
    public class RenderPacket
    {
        /// <summary>
        /// Constructs a new instance of RenderPacket with the byte array of the render message.
        /// </summary>
        /// <param name="bytes">The bytes of the render message.</param>
        public RenderPacket(byte[] bytes)
        {
            Bytes = bytes;
        }

        /// <summary>
        /// Gets the bytes of the render message.
        /// </summary>
        public byte[] Bytes { get; }

        /// <summary>
        /// Determines the equality of the RenderPacket and the other object.
        /// </summary>
        /// <param name="obj">The object to test equality with.</param>
        /// <returns>Returns true if the objects are equal, false otherwise.</returns>
        public override bool Equals(object obj)
        {
            if (this == obj) return true;
            if (obj == null || GetType() != obj.GetType()) return false;
            RenderPacket that = (RenderPacket)obj;
            return Bytes.SequenceEqual(that.Bytes);
        }

        /// <summary>
        /// Gets the hash code of the RenderPacket.
        /// </summary>
        /// <returns>Returns the hashcode of the RenderPacket.</returns>
        public override int GetHashCode()
        {
            return ((IStructuralEquatable)Bytes).GetHashCode(EqualityComparer<byte>.Default);
        }
    }
}