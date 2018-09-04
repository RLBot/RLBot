using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class BallState
    {
        public PhysicsState PhysicsState;

        public BallState()
        {

        }

        public BallState(PhysicsState physicsState)
        {
            PhysicsState = physicsState;
        }

        public Offset<DesiredBallState> ToFlatBuffer(FlatBufferBuilder builder)
        {
            int physicsStateOffset = PhysicsState == null ? -1 : PhysicsState.ToFlatBuffer(builder).Value;

            DesiredBallState.StartDesiredBallState(builder);

            if (PhysicsState != null)
                DesiredBallState.AddPhysics(builder, new Offset<DesiredPhysics>(physicsStateOffset));

            return DesiredBallState.EndDesiredBallState(builder);
        }
    }
}
