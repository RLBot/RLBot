package rlbot.gamestate;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.flat.DesiredPhysics;
import rlbot.vector.Vector3;

/**
 * See https://github.com/RLBot/RLBotJavaExample/wiki/Manipulating-Game-State
 */
public class PhysicsState {
    private DesiredVector3 location;
    private DesiredRotation rotation;
    private DesiredVector3 velocity;
    private DesiredVector3 angularVelocity;

    public PhysicsState() {
    }

    public PhysicsState(DesiredVector3 location, DesiredRotation rotation, DesiredVector3 velocity, DesiredVector3 angularVelocity) {
        this.location = location;
        this.rotation = rotation;
        this.velocity = velocity;
        this.angularVelocity = angularVelocity;
    }

    public DesiredVector3 getLocation() {
        return location;
    }

    public PhysicsState withLocation(DesiredVector3 location) {
        this.location = location;
        return this;
    }

    public DesiredRotation getRotation() {
        return rotation;
    }

    public PhysicsState withRotation(DesiredRotation rotation) {
        this.rotation = rotation;
        return this;
    }

    public DesiredVector3 getVelocity() {
        return velocity;
    }

    public PhysicsState withVelocity(DesiredVector3 velocity) {
        this.velocity = velocity;
        return this;
    }

    public DesiredVector3 getAngularVelocity() {
        return angularVelocity;
    }

    public PhysicsState withAngularVelocity(DesiredVector3 angularVelocity) {
        this.angularVelocity = angularVelocity;
        return this;
    }


    public int toFlatbuffer(FlatBufferBuilder builder) {

        Integer locationOffset = location == null ? null : location.toFlatbuffer(builder);
        Integer rotationOffset = rotation == null ? null : rotation.toFlatbuffer(builder);
        Integer velocityOffset = velocity == null ? null : velocity.toFlatbuffer(builder);
        Integer angularVelocityOffset = angularVelocity == null ? null : angularVelocity.toFlatbuffer(builder);


        DesiredPhysics.startDesiredPhysics(builder);
        if (locationOffset != null) {
            DesiredPhysics.addLocation(builder, locationOffset);
        }
        if (rotationOffset != null) {
            DesiredPhysics.addRotation(builder, rotationOffset);
        }
        if (velocityOffset != null) {
            DesiredPhysics.addVelocity(builder, velocityOffset);
        }
        if (angularVelocityOffset != null) {
            DesiredPhysics.addAngularVelocity(builder, angularVelocityOffset);
        }

        return DesiredPhysics.endDesiredPhysics(builder);
    }





}
