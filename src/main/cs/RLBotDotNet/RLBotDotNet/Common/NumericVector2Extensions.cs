using FlatBuffers;
using rlbot.flat;

namespace RLBotDotNet.Common
{
    /// <summary>
    /// Extension methods for <see cref="System.Numerics.Vector2"/>.
    /// </summary>
    public static class NumericVector2Extensions
    {
        /// <summary>
        /// Converts the <see cref="System.Numerics.Vector2"/> to offset vector with the given <see cref="FlatBufferBuilder"/>.
        /// </summary>
        /// <param name="vector2">The <see cref="System.Numerics.Vector2"/> to convert.</param>
        /// <param name="builder">The <see cref="FlatBufferBuilder"/> to use to create the offset vector.</param>
        /// <returns>The created offset vector from the <see cref="System.Numerics.Vector2"/>.</returns>
        public static Offset<Vector3> ToOffsetVector(this System.Numerics.Vector2 vector2, FlatBufferBuilder builder)
        {
            return Vector3.CreateVector3(builder, vector2.X, vector2.Y, 0);
        }
    }
}