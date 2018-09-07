﻿using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class BallState
    {
<<<<<<< HEAD
        private PhysicsState physicsState;

        public PhysicsState PhysicsState
        {
            get
            {
                if (physicsState == null)
                    physicsState = new PhysicsState();

                return physicsState;
            }

            set
            {
                physicsState = value;
            }
        }

        public BallState(PhysicsState physicsState = null)
        {
            PhysicsState = physicsState;
        }

        public BallState(BallInfo ballInfo)
        {
            if (ballInfo.Physics.HasValue)
                PhysicsState = new PhysicsState(ballInfo.Physics.Value);
=======
        public PhysicsState PhysicsState;

        public BallState()
        {

        }

        public BallState(PhysicsState physicsState)
        {
            PhysicsState = physicsState;
>>>>>>> upstream/master
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