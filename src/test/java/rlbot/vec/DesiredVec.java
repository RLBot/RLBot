package rlbot.vec;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.flat.Vector3Partial;
import rlbot.gamestate.DesiredVector3;

public class DesiredVec extends DesiredVector3 {

    @Override
    public int toFlatbuffer(FlatBufferBuilder builder) {
        Vector3Partial.startVector3Partial(builder);
        if (getX() != null) {
            // Invert X because we invert it in the Vector3 class also.
            Vector3Partial.addX(builder, rlbot.flat.Float.createFloat(builder, -getX()));
        }
        if (getY() != null) {
            Vector3Partial.addY(builder, rlbot.flat.Float.createFloat(builder, getY()));
        }
        if (getZ() != null) {
            Vector3Partial.addZ(builder, rlbot.flat.Float.createFloat(builder, getZ()));
        }
        return Vector3Partial.endVector3Partial(builder);
    }
}
