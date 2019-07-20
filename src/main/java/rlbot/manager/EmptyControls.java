package rlbot.manager;

import rlbot.ControllerState;

public class EmptyControls implements ControllerState {
    @Override
    public float getSteer() {
        return 0;
    }

    @Override
    public float getThrottle() {
        return 0;
    }

    @Override
    public float getPitch() {
        return 0;
    }

    @Override
    public float getYaw() {
        return 0;
    }

    @Override
    public float getRoll() {
        return 0;
    }

    @Override
    public boolean holdJump() {
        return false;
    }

    @Override
    public boolean holdBoost() {
        return false;
    }

    @Override
    public boolean holdHandbrake() {
        return false;
    }

    @Override
    public boolean holdUseItem() {
        return false;
    }
}
