package rlbot.vec;

import com.google.flatbuffers.FlatBufferBuilder;

public class Vector3 extends rlbot.vector.Vector3 {

    public Vector3(float x, float y, float z) {
        super(x, y, z);
    }

    public Vector3(double x, double y, double z) {
        super((float) x, (float) y, (float) z);
    }

    public int toFlatbuffer(FlatBufferBuilder builder) {
        return rlbot.flat.Vector3.createVector3(builder, -x, y, z);
    }

    public static Vector3 fromFlatbuffer(rlbot.flat.Vector3 vec) {
        // Invert the X value so that the axes make more sense.
        return new Vector3(-vec.x(), vec.y(), vec.z());
    }

    public Vector3() {
        this(0, 0, 0);
    }

    public Vector3 plus(Vector3 other) {
        return new Vector3(x + other.x, y + other.y, z + other.z);
    }

    public Vector3 minus(Vector3 other) {
        return new Vector3(x - other.x, y - other.y, z - other.z);
    }

    public Vector3 scaled(float scale) {
        return new Vector3(x * scale, y * scale, z * scale);
    }

    /**
     * If magnitude is negative, we will return a vector facing the opposite direction.
     */
    public Vector3 scaledToMagnitude(float magnitude) {
        if (isZero()) {
            throw new IllegalStateException("Cannot scale up a vector with length zero!");
        }
        float scaleRequired = magnitude / magnitude();
        return scaled(scaleRequired);
    }

    public double distance(Vector3 other) {
        double xDiff = x - other.x;
        double yDiff = y - other.y;
        double zDiff = z - other.z;
        return Math.sqrt(xDiff * xDiff + yDiff * yDiff + zDiff * zDiff);
    }

    public float magnitude() {
        return (float) Math.sqrt(magnitudeSquared());
    }

    public float magnitudeSquared() {
        return x * x + y * y + z * z;
    }

    public Vector3 normalized() {

        if (isZero()) {
            throw new IllegalStateException("Cannot normalize a vector with length zero!");
        }
        return this.scaled(1 / magnitude());
    }

    public double dotProduct(Vector3 other) {
        return x * other.x + y * other.y + z * other.z;
    }

    public boolean isZero() {
        return x == 0 && y == 0 && z == 0;
    }

    public Vector2 flatten() {
        return new Vector2(x, y);
    }

    public float angle(Vector3 v) {
        double mag2 = magnitudeSquared();
        double vmag2 = v.magnitudeSquared();
        double dot = dotProduct(v);
        return (float) Math.acos(dot / Math.sqrt(mag2 * vmag2));
    }

    public Vector3 crossProduct(Vector3 v) {
        float tx = y * v.z - z * v.y;
        float ty = z * v.x - x * v.z;
        float tz = x * v.y - y * v.x;
        return new Vector3(tx, ty, tz);
    }
}
