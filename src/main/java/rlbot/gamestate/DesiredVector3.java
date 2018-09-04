package rlbot.gamestate;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.flat.Vector3Partial;

/**
 * See https://github.com/RLBot/RLBotJavaExample/wiki/Manipulating-Game-State
 */
public class DesiredVector3 {
    private Float x;
    private Float y;
    private Float z;

    public DesiredVector3() {
    }

    public DesiredVector3(Float x, Float y, Float z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    public Float getX() {
        return x;
    }

    public DesiredVector3 withX(Float x) {
        this.x = x;
        return this;
    }

    public Float getY() {
        return y;
    }

    public DesiredVector3 withY(Float y) {
        this.y = y;
        return this;
    }

    public Float getZ() {
        return z;
    }

    public DesiredVector3 withZ(Float z) {
        this.z = z;
        return this;
    }

    /**
     * You may wish to override this in order to invert the x value, which would give you a normal
     * right-handed coordinate system.
     */
    public int toFlatbuffer(FlatBufferBuilder builder) {
        Vector3Partial.startVector3Partial(builder);
        if (x != null) {
            Vector3Partial.addX(builder, rlbot.flat.Float.createFloat(builder, x));
        }
        if (y != null) {
            Vector3Partial.addY(builder, rlbot.flat.Float.createFloat(builder, y));
        }
        if (z != null) {
            Vector3Partial.addZ(builder, rlbot.flat.Float.createFloat(builder, z));
        }
        return Vector3Partial.endVector3Partial(builder);
    }
}
