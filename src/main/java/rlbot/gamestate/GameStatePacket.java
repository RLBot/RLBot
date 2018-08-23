package rlbot.gamestate;

import java.util.Arrays;

public class GameStatePacket {

    private final byte[] bytes;

    GameStatePacket(byte[] bytes) {
        this.bytes = bytes;
    }

    public byte[] getBytes() {
        return bytes;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        GameStatePacket that = (GameStatePacket) o;
        return Arrays.equals(bytes, that.bytes);
    }

    @Override
    public int hashCode() {
        return Arrays.hashCode(bytes);
    }
}
