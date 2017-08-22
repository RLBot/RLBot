package rlbot;

public class AgentOutput {

    public static final int MAX_TILT = 32767;

    // 0 is straight, -1 is hard left, 1 is hard right.
    private float steeringTilt;
    private float pitchTilt;

    // 0 is none, 1 is full
    private float acceleration;
    private float deceleration;

    private boolean jumpDepressed;
    private boolean boostDepressed;
    private boolean slideDepressed;

    public AgentOutput() {
    }

    /**
     * -1 for hard left, 1 for hard right.
     */
    public AgentOutput withSteer(float steeringTilt) {
        this.steeringTilt = steeringTilt;
        return this;
    }

    /**
     * -1 for nose down hard, 1 for nose up hard
     */
    public AgentOutput withPitch(float pitchTilt) {
        this.pitchTilt = pitchTilt;
        return this;
    }

    /**
     * 1 for full acceleration, 0 to stand still.
     */
    public AgentOutput withAcceleration(float acceleration) {
        this.acceleration = acceleration;
        return this;
    }

    /**
     * 1 for full reverse, 0 to stand still.
     */
    public AgentOutput withDeceleration(float deceleration) {
        this.deceleration = deceleration;
        return this;
    }

    public AgentOutput withJump(boolean jumpDepressed) {
        this.jumpDepressed = jumpDepressed;
        return this;
    }

    public AgentOutput withBoost(boolean boostDepressed) {
        this.boostDepressed = boostDepressed;
        return this;
    }

    public AgentOutput withSlide(boolean slideDepressed) {
        this.slideDepressed = slideDepressed;
        return this;
    }


    public int[] toPython() {
        return new int[] {
                convertMagnitudeWithNegatives(steeringTilt),
                convertMagnitudeWithNegatives(pitchTilt),
                convertMagnitudeOnlyPositive(acceleration),
                convertMagnitudeOnlyPositive(deceleration),
                jumpDepressed ? 1 : 0,
                boostDepressed ? 1 : 0,
                slideDepressed ? 1 : 0
        };
    }

    private int convertMagnitudeWithNegatives(float tilt) {
        float normalized = (tilt + 1) / 2;
        return convertMagnitudeOnlyPositive(normalized);
    }

    private int convertMagnitudeOnlyPositive(float normalized) {
        float intScaled = normalized * MAX_TILT;
        return Math.round(intScaled);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        AgentOutput that = (AgentOutput) o;

        if (Float.compare(that.steeringTilt, steeringTilt) != 0) return false;
        if (Float.compare(that.pitchTilt, pitchTilt) != 0) return false;
        if (Float.compare(that.acceleration, acceleration) != 0) return false;
        if (Float.compare(that.deceleration, deceleration) != 0) return false;
        if (jumpDepressed != that.jumpDepressed) return false;
        if (boostDepressed != that.boostDepressed) return false;
        return slideDepressed == that.slideDepressed;
    }

    @Override
    public int hashCode() {
        int result = (steeringTilt != +0.0f ? Float.floatToIntBits(steeringTilt) : 0);
        result = 31 * result + (pitchTilt != +0.0f ? Float.floatToIntBits(pitchTilt) : 0);
        result = 31 * result + (acceleration != +0.0f ? Float.floatToIntBits(acceleration) : 0);
        result = 31 * result + (deceleration != +0.0f ? Float.floatToIntBits(deceleration) : 0);
        result = 31 * result + (jumpDepressed ? 1 : 0);
        result = 31 * result + (boostDepressed ? 1 : 0);
        result = 31 * result + (slideDepressed ? 1 : 0);
        return result;
    }
}
