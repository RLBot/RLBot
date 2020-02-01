using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class BallState
    {
        private PhysicsState physicsState;

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

        public BallState(PhysicsState physicsState = null)
        {
            PhysicsState = physicsState;
        }

        public BallState(BallInfo ballInfo)
        {
            if (ballInfo.Physics.HasValue)
                PhysicsState = new PhysicsState(ballInfo.Physics.Value);
        }

        public Offset<DesiredBallState> ToFlatBuffer(FlatBufferBuilder builder)
        {
            int physicsStateOffset = PhysicsState?.ToFlatBuffer(builder).Value ?? -1;

            DesiredBallState.StartDesiredBallState(builder);

            if (PhysicsState != null)
                DesiredBallState.AddPhysics(builder, new Offset<DesiredPhysics>(physicsStateOffset));

            return DesiredBallState.EndDesiredBallState(builder);
        }
    }
}