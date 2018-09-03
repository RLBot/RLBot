package rlbot.gamestate;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.flat.RotatorPartial;

/**
 * See https://github.com/RLBot/RLBotJavaExample/wiki/Manipulating-Game-State
 */
public class DesiredRotation {
    public final Float pitch;
    public final Float yaw;
    public final Float roll;

    public DesiredRotation(Float pitch, Float yaw, Float roll) {
        this.pitch = pitch;
        this.yaw = yaw;
        this.roll = roll;
    }

    public DesiredRotation(rlbot.flat.Rotator rot) {
        this(rot.pitch(), rot.yaw(), rot.roll());
    }

    public int toFlatbuffer(FlatBufferBuilder builder) {
        RotatorPartial.startRotatorPartial(builder);
        if (pitch != null) {
            RotatorPartial.addPitch(builder, rlbot.flat.Float.createFloat(builder, pitch));
        }
        if (yaw != null) {
            RotatorPartial.addYaw(builder, rlbot.flat.Float.createFloat(builder, yaw));
        }
        if (roll != null) {
            RotatorPartial.addRoll(builder, rlbot.flat.Float.createFloat(builder, roll));
        }
        return RotatorPartial.endRotatorPartial(builder);
    }
}
