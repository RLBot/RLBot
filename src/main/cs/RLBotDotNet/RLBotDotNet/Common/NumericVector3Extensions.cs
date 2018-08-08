using FlatBuffers;
using rlbot.flat;

namespace RLBotDotNet.Common
{
    /// <summary>
    /// Extension methods for <see cref="System.Numerics.Vector3"/>.
    /// </summary>
    public static class NumericVector3Extensions
    {
        /// <summary>
        /// Converts the <see cref="System.Numerics.Vector3"/> to offset vector with the given <see cref="FlatBufferBuilder"/>.
        /// </summary>
        /// <param name="vector3">The <see cref="System.Numerics.Vector3"/> to convert.</param>
        /// <param name="builder">The <see cref="FlatBufferBuilder"/> to use to create the offset vector.</param>
        /// <returns>The created offset vector from the <see cref="System.Numerics.Vector3"/>.</returns>
        public static Offset<Vector3> ToOffsetVector(this System.Numerics.Vector3 vector3, FlatBufferBuilder builder)
        {
            return Vector3.CreateVector3(builder, vector3.X, vector3.Y, vector3.Z);
        }
    }
}