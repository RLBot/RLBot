using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class CarState
    {
        private PhysicsState physicsState;

        public bool? Jumped;
        public bool? DoubleJumped;
        public float? Boost;

        public PhysicsState PhysicsState
        {
            get
            {
                if (physicsState == null)
                    physicsState = new PhysicsState();

                return physicsState;
            }

            set => physicsState = value;
        }

        public CarState(PhysicsState physicsState = null, bool? jumped = null, bool? doubleJumped = null, float? boost = null)
        {
            PhysicsState = physicsState;
            Jumped = jumped;
            DoubleJumped = doubleJumped;
            Boost = boost;
        }

        public CarState(PlayerInfo playerInfo)
        {
            if (playerInfo.Physics.HasValue)
                PhysicsState = new PhysicsState(playerInfo.Physics.Value);

            Jumped = playerInfo.Jumped;
            DoubleJumped = playerInfo.DoubleJumped;
            Boost = playerInfo.Boost;
        }

        public Offset<DesiredCarState> ToFlatBuffer(FlatBufferBuilder builder)
        {
            int physicsStateOffset = PhysicsState?.ToFlatBuffer(builder).Value ?? -1;

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