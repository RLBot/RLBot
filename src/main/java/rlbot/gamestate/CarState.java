package rlbot.gamestate;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.flat.Bool;
import rlbot.flat.DesiredCarState;

/**
 * See https://github.com/RLBot/RLBotJavaExample/wiki/Manipulating-Game-State
 */
public class CarState {
    private PhysicsState physics;
    private Boolean jumped;
    private Boolean doubleJumped;
    private Float boostAmount;

    public CarState() {
    }

    public CarState(PhysicsState physics, Boolean jumped, Boolean doubleJumped, Float boostAmount) {
        this.physics = physics;
        this.jumped = jumped;
        this.doubleJumped = doubleJumped;
        this.boostAmount = boostAmount;
    }

    public PhysicsState getPhysics() {
        return physics;
    }

    public CarState withPhysics(PhysicsState physics) {
        this.physics = physics;
        return this;
    }

    public Boolean getJumped() {
        return jumped;
    }

    public CarState withJumped(Boolean jumped) {
        this.jumped = jumped;
        return this;
    }

    public Boolean getDoubleJumped() {
        return doubleJumped;
    }

    public CarState withDoubleJumped(Boolean doubleJumped) {
        this.doubleJumped = doubleJumped;
        return this;
    }

    public Float getBoostAmount() {
        return boostAmount;
    }

    public CarState withBoostAmount(Float boostAmount) {
        this.boostAmount = boostAmount;
        return this;
    }

    public int toFlatbuffer(FlatBufferBuilder builder) {

        Integer physicsOffset = physics == null ? null : physics.toFlatbuffer(builder);

        DesiredCarState.startDesiredCarState(builder);
        if (physicsOffset != null) {
            DesiredCarState.addPhysics(builder, physicsOffset);
        }
        if (jumped != null) {
            DesiredCarState.addJumped(builder, Bool.createBool(builder, jumped));
        }
        if (doubleJumped != null) {
            DesiredCarState.addDoubleJumped(builder, Bool.createBool(builder, doubleJumped));
        }
        if (boostAmount != null) {
            DesiredCarState.addBoostAmount(builder, rlbot.flat.Float.createFloat(builder, boostAmount));
        }
        return DesiredCarState.endDesiredCarState(builder);
    }
}
