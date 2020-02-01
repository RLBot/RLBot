using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class PhysicsState
    {
        private DesiredVector3 location;
        private DesiredVector3 velocity;
        private DesiredRotator rotation;
        private DesiredVector3 angularVelocity;

        #region Getters/Setters

        public DesiredVector3 Location
        {
            get
            {
                if (location == null)
                    location = new DesiredVector3();

                return location;
            }

            set => location = value;
        }

        public DesiredVector3 Velocity
        {
            get
            {
                if (velocity == null)
                    velocity = new DesiredVector3();

                return velocity;
            }

            set => velocity = value;
        }

        public DesiredRotator Rotation
        {
            get
            {
                if (rotation == null)
                    rotation = new DesiredRotator();

                return rotation;
            }

            set => rotation = value;
        }

        public DesiredVector3 AngularVelocity
        {
            get
            {
                if (angularVelocity == null)
                    angularVelocity = new DesiredVector3();

                return angularVelocity;
            }

            set => angularVelocity = value;
        }

        #endregion

        public PhysicsState(DesiredVector3 location = null, DesiredVector3 velocity = null, DesiredRotator rotation = null,
            DesiredVector3 angularVelocity = null)
        {
            Location = location;
            Velocity = velocity;
            Rotation = rotation;
            AngularVelocity = angularVelocity;
        }

        public PhysicsState(Physics physics)
        {
            if (physics.Location.HasValue)
                Location = new DesiredVector3(physics.Location.Value);

            if (physics.Velocity.HasValue)
                Velocity = new DesiredVector3(physics.Velocity.Value);

            if (physics.Rotation.HasValue)
                Rotation = new DesiredRotator(physics.Rotation.Value);

            if (physics.AngularVelocity.HasValue)
                AngularVelocity = new DesiredVector3(physics.AngularVelocity.Value);
        }

        public Offset<DesiredPhysics> ToFlatBuffer(FlatBufferBuilder builder)
        {
            int locationOffset = Location?.ToFlatBuffer(builder).Value ?? -1;
            int velocityOffset = Velocity?.ToFlatBuffer(builder).Value ?? -1;
            int rotationOffset = Rotation?.ToFlatBuffer(builder).Value ?? -1;
            int angularVelocityOffset = AngularVelocity?.ToFlatBuffer(builder).Value ?? -1;

            DesiredPhysics.StartDesiredPhysics(builder);

            if (Location != null)
                DesiredPhysics.AddLocation(builder, new Offset<Vector3Partial>(locationOffset));

            if (Velocity != null)
                DesiredPhysics.AddVelocity(builder, new Offset<Vector3Partial>(velocityOffset));

            if (Rotation != null)
                DesiredPhysics.AddRotation(builder, new Offset<RotatorPartial>(rotationOffset));

            if (AngularVelocity != null)
                DesiredPhysics.AddAngularVelocity(builder, new Offset<Vector3Partial>(angularVelocityOffset));

            return DesiredPhysics.EndDesiredPhysics(builder);
        }
    }
}