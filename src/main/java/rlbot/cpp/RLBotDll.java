package rlbot.cpp;

import com.google.protobuf.InvalidProtocolBufferException;
import com.sun.jna.Memory;
import com.sun.jna.Native;
import com.sun.jna.Pointer;
import rlbot.api.GameData;

public class RLBotDll {

    private static native ByteBufferStruct UpdateLiveDataPacketProto();
    private static native int UpdatePlayerInputProto(Pointer ptr, int size, int playerIndex);

    static {
        Native.register("RLBot_Core_Interface");
    }

    public static GameData.GameTickPacket getProtoPacket() throws InvalidProtocolBufferException {
        ByteBufferStruct struct = UpdateLiveDataPacketProto();
        byte[] protoBytes = struct.ptr.getByteArray(0, struct.size);
        GameData.GameTickPacket packet = GameData.GameTickPacket.parseFrom(protoBytes);

        return packet;
    }

    public static void setControllerState(GameData.ControllerState controllerState, int playerIndex) {
        byte[] protoBytes = controllerState.toByteArray();
        Memory memory = getMemory(protoBytes);
        UpdatePlayerInputProto(memory, protoBytes.length, playerIndex);
    }

    private static Memory getMemory(byte[] protoBytes) {
        final Memory mem = new Memory(protoBytes.length);
        mem.write(0, protoBytes, 0, protoBytes.length);
        return mem;
    }

}
