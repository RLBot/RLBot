package rlbot.vector;

import com.google.flatbuffers.FlatBufferBuilder;

public class Vector3 {
    public final float x;
    public final float y;
    public final float z;

    public Vector3(float x, float y, float z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    /**
     * You may wish to override this in order to invert the x value, which would give you a normal
     * right-handed coordinate system.
     */
    public Vector3(rlbot.flat.Vector3 vec) {
        this(vec.x(), vec.y(), vec.z());
    }

    /**
     * If you overrode the flatbuffer constructor, you probably want to override this too.
     */
    public int toFlatbuffer(FlatBufferBuilder builder) {
        return rlbot.flat.Vector3.createVector3(builder, x, y, z);
    }
}
