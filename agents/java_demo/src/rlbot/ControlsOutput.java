package rlbot;

import rlbot.api.GameData;

public class ControlsOutput {

    // 0 is straight, -1 is hard left, 1 is hard right.
    private float steer;

    // -1 for front flip, 1 for back flip
    private float pitch;

    // 0 is straight, -1 is hard left, 1 is hard right.
    private float yaw;

    // 0 is straight, -1 is hard left, 1 is hard right.
    private float roll;

    // 0 is none, -1 is backwards, 1 is forwards
    private float throttle;

    private boolean jumpDepressed;
    private boolean boostDepressed;
    private boolean slideDepressed;

    public ControlsOutput() {
    }

    public ControlsOutput withSteer(float steer) {
        this.steer = clamp(steer);
        return this;
    }

    public ControlsOutput withPitch(float pitch) {
        this.pitch = clamp(pitch);
        return this;
    }

    public ControlsOutput withYaw(float yaw) {
        this.yaw = clamp(yaw);
        return this;
    }

    public ControlsOutput withRoll(float roll) {
        this.roll = clamp(roll);
        return this;
    }

    public ControlsOutput withThrottle(float throttle) {
        this.throttle = clamp(throttle);
        return this;
    }

    public ControlsOutput withJump(boolean jumpDepressed) {
        this.jumpDepressed = jumpDepressed;
        return this;
    }

    public ControlsOutput withBoost(boolean boostDepressed) {
        this.boostDepressed = boostDepressed;
        return this;
    }

    public ControlsOutput withSlide(boolean slideDepressed) {
        this.slideDepressed = slideDepressed;
        return this;
    }

    public ControlsOutput withJump() {
        this.jumpDepressed = true;
        return this;
    }

    public ControlsOutput withBoost() {
        this.boostDepressed = true;
        return this;
    }

    public ControlsOutput withSlide() {
        this.slideDepressed = true;
        return this;
    }

    private float clamp(float value) {
        return Math.max(-1, Math.min(1, value));
    }

    GameData.ControllerState toControllerState() {
        return GameData.ControllerState.newBuilder()
                .setThrottle(throttle)
                .setSteer(steer)
                .setPitch(pitch)
                .setYaw(yaw)
                .setRoll(roll)
                .setBoost(boostDepressed)
                .setHandbrake(slideDepressed)
                .setJump(jumpDepressed)
                .build();
    }
}
