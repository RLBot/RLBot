package rlbot.cpp;

import com.sun.jna.Memory;
import com.sun.jna.Native;
import com.sun.jna.Pointer;
import rlbot.api.GameData;

import java.io.IOException;

public class RLBotDll {

    private static native ByteBufferStruct UpdateLiveDataPacketProto();
    private static native int UpdatePlayerInputProto(Pointer ptr, int size, int playerIndex);

    static {
        Native.register("RLBot_Core_Interface");
    }

    public static GameData.GameTickPacket getProtoPacket() throws IOException {
        try {
            final ByteBufferStruct struct = UpdateLiveDataPacketProto();
            final byte[] protoBytes = struct.ptr.getByteArray(0, struct.size);
            return GameData.GameTickPacket.parseFrom(protoBytes);
        } catch (final Error error) {
            throw new IOException(error);
        }
    }

    public static void setControllerState(GameData.ControllerState controllerState, int playerIndex) {
        final byte[] protoBytes = controllerState.toByteArray();
        final Memory memory = getMemory(protoBytes);
        UpdatePlayerInputProto(memory, protoBytes.length, playerIndex);
    }

    private static Memory getMemory(byte[] protoBytes) {
        if (protoBytes.length == 0) {
            // The empty controller state is actually 0 bytes, so this can happen.
            // You're not allowed to pass 0 bytes to the Memory constructor, so do this.
            return new Memory(1);
        }

        final Memory mem = new Memory(protoBytes.length);
        mem.write(0, protoBytes, 0, protoBytes.length);
        return mem;
    }

}
