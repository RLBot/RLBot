package rlbot.vector;

import com.google.flatbuffers.FlatBufferBuilder;

/**
 * Holds x, y, and z coordinates. This class provides a standard way of representing this data
 * so that the rendering feature can be streamlined. It is recommended that you extend this class
 * with helpful vector math methods so that it becomes useful in your bot logic.
 *
 * Alternatively, you can use your own vector representation and just translate to this class
 * when you want to render something.
 */
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
