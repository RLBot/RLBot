using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class DesiredRotator
    {
        public float? Pitch;
        public float? Yaw;
        public float? Roll;

        public DesiredRotator(float? pitch = null, float? yaw = null, float? roll = null)
        {
            Pitch = pitch;
            Yaw = yaw;
            Roll = roll;
        }

        public DesiredRotator(Rotator rotator)
        {
            Pitch = rotator.Pitch;
            Yaw = rotator.Yaw;
            Roll = rotator.Roll;
        }

        public Offset<RotatorPartial> ToFlatBuffer(FlatBufferBuilder builder)
        {
            RotatorPartial.StartRotatorPartial(builder);

            if (Pitch.HasValue)
                RotatorPartial.AddPitch(builder, Float.CreateFloat(builder, Pitch.Value));

            if (Yaw.HasValue)
                RotatorPartial.AddYaw(builder, Float.CreateFloat(builder, Yaw.Value));

            if (Roll.HasValue)
                RotatorPartial.AddRoll(builder, Float.CreateFloat(builder, Roll.Value));

            return RotatorPartial.EndRotatorPartial(builder);
        }
    }
}