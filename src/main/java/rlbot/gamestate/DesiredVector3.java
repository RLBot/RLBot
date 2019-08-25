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
    
    /**
     * @returns {@code true} If x is not null.
     */
    public boolean hasX() {
        return x != null
    }

    public DesiredVector3 withX(Float x) {
        this.x = x;
        return this;
    }

    public Float getY() {
        return y;
    }
    
    /**
     * @returns {@code true} If y is not null.
     */
    public boolean hasY() {
        return y != null
    }

    public DesiredVector3 withY(Float y) {
        this.y = y;
        return this;
    }

    public Float getZ() {
        return z;
    }
    
    /**
     * @returns {@code true} If z is not null.
     */
    public boolean hasZ() {
        return z != null
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
        if (hasX()) {
            Vector3Partial.addX(builder, rlbot.flat.Float.createFloat(builder, getX()));
        }
        if (hasY()) {
            Vector3Partial.addY(builder, rlbot.flat.Float.createFloat(builder, getY()));
        }
        if (hasZ()) {
            Vector3Partial.addZ(builder, rlbot.flat.Float.createFloat(builder, getZ()));
        }
        return Vector3Partial.endVector3Partial(builder);
    }
}
