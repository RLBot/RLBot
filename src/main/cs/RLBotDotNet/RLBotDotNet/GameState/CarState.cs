using System;

using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class CarState
    {
        public PhysicsState PhysicsState;
        public bool? Jumped;
        public bool? DoubleJumped;
        public float? Boost;

        public CarState()
        {

        }

        public Offset<DesiredCarState> ToFlatBuffer(FlatBufferBuilder builder)
        {
            int physicsStateOffset = PhysicsState == null ? -1 : PhysicsState.ToFlatBuffer(builder).Value;

            DesiredCarState.StartDesiredCarState(builder);

            if (PhysicsState != null)
                DesiredCarState.AddPhysics(builder, new Offset<DesiredPhysics>(physicsStateOffset));

            if (Jumped.HasValue)
                DesiredCarState.AddJumped(builder, Bool.CreateBool(builder, Jumped.Value));

            if (DoubleJumped.HasValue)
                DesiredCarState.AddDoubleJumped(builder, Bool.CreateBool(builder, DoubleJumped.Value));

            if (Boost.HasValue)
                DesiredCarState.AddBoostAmount(builder, Float.CreateFloat(builder, Boost.Value));

            return DesiredCarState.EndDesiredCarState(builder);
        }
    }
}
