﻿using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class DesiredVector3
    {
        public float? X;
        public float? Y;
        public float? Z;

        public DesiredVector3()
        {

        }

        public DesiredVector3(float x, float y, float z)
        {
            X = x;
            Y = y;
            Z = z;
        }

        public DesiredVector3(Vector3 vector)
        {
            X = vector.X;
            Y = vector.Y;
            Z = vector.Z;
        }

        public Offset<Vector3Partial> ToFlatBuffer(FlatBufferBuilder builder)
        {
            Vector3Partial.StartVector3Partial(builder);

            if (X.HasValue)
                Vector3Partial.AddX(builder, Float.CreateFloat(builder, X.Value));

            if (Y.HasValue)
                Vector3Partial.AddY(builder, Float.CreateFloat(builder, Y.Value));

            if (Z.HasValue)
                Vector3Partial.AddZ(builder, Float.CreateFloat(builder, Z.Value));

            return Vector3Partial.EndVector3Partial(builder);
        }
    }
}
