package rlbot;

/**
 * Holds all the data needed to control a car for one frame. This will be used
 * when transmitting a bot's intentions back to the game.
 */
public interface ControllerState {

    /**
     * 0 is straight, -1 is hard left, 1 is hard right.
     */
    float getSteer();

    /**
     * 0 is none, -1 is backwards, 1 is forwards
     */
    float getThrottle();

    /**
     * -1 for front flip, 1 for back flip@return
     */
    float getPitch();

    /**
     * 0 is straight, -1 is hard left, 1 is hard right.
     */
    float getYaw();

    /**
     * 0 is straight, -1 is hard left, 1 is hard right.
     */
    float getRoll();

    /**
     * True to hold jump
     */
    boolean holdJump();

    /**
     * True to hold boost
     */
    boolean holdBoost();

    /**
     * True to hold handbrake
     */
    boolean holdHandbrake();

}
