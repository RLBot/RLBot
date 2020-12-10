package rlbot.flatutil;

import rlbot.flat.GameTickPacket;

import java.nio.ByteBuffer;

public class GameTickPacketWrapper {

    public final byte[] underlyingData;
    public final GameTickPacket gameTickPacket;

    public GameTickPacketWrapper(final byte[] data) {
        underlyingData = data.clone();
        gameTickPacket = GameTickPacket.getRootAsGameTickPacket(ByteBuffer.wrap(underlyingData));
    }
}
