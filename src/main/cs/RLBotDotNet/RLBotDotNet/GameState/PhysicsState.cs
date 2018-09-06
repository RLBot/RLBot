using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class PhysicsState
    {
        public DesiredVector3 Location;
        public DesiredVector3 Velocity;
        public DesiredRotator Rotation;
        public DesiredVector3 AngularVelocity;

        public PhysicsState()
        {

        }

        public PhysicsState(DesiredVector3 location, DesiredVector3 velocity, DesiredRotator rotation, DesiredVector3 angularVelocity)
        {
            Location = location;
            Velocity = velocity;
            Rotation = rotation;
            AngularVelocity = angularVelocity;
        }

        public Offset<DesiredPhysics> ToFlatBuffer(FlatBufferBuilder builder)
        {
            int locationOffset = Location == null ? -1 : Location.ToFlatBuffer(builder).Value;
            int velocityOffset = Velocity == null ? -1 : Velocity.ToFlatBuffer(builder).Value;
            int rotationOffset = Rotation == null ? -1 : Rotation.ToFlatBuffer(builder).Value;
            int angularVelocityOffset = AngularVelocity == null ? -1 : AngularVelocity.ToFlatBuffer(builder).Value;

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
