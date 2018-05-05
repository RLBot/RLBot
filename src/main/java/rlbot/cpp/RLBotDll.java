package rlbot.cpp;

import com.google.flatbuffers.FlatBufferBuilder;
import com.sun.jna.Memory;
import com.sun.jna.Native;
import com.sun.jna.Pointer;
import rlbot.ControllerState;
import rlbot.api.GameData;
import rlbot.flat.GameTickPacket;

import java.io.IOException;
import java.nio.ByteBuffer;

public class RLBotDll {

    private static native ByteBufferStruct UpdateLiveDataPacketProto();
    private static native int UpdatePlayerInputProto(Pointer ptr, int size);

    private static native ByteBufferStruct UpdateLiveDataPacketFlatbuffer();
    private static native int UpdatePlayerInputFlatbuffer(Pointer ptr, int size);

    static {
        Native.register("RLBot_Core_Interface");
    }

    public static GameTickPacket getFlatbufferPacket() throws IOException {
        try {
            final ByteBufferStruct struct = UpdateLiveDataPacketFlatbuffer();
            if (struct.size < 4) {
                throw new IOException("Flatbuffer packet is too small, match is probably not running!");
            }
            final byte[] protoBytes = struct.ptr.getByteArray(0, struct.size);
            return GameTickPacket.getRootAsGameTickPacket(ByteBuffer.wrap(protoBytes));
        } catch (final Error error) {
            throw new IOException(error);
        }
    }

    public static GameData.GameTickPacket getProtobufPacket() throws IOException {
        try {
            final ByteBufferStruct struct = UpdateLiveDataPacketProto();
            final byte[] protoBytes = struct.ptr.getByteArray(0, struct.size);
            return GameData.GameTickPacket.parseFrom(protoBytes);
        } catch (final Error error) {
            throw new IOException(error);
        }
    }

    /**
     * Set player input in flatbuffer format.
     */
    public static void setPlayerInputFlatbuffer(ControllerState controllerState, int index) {

        FlatBufferBuilder builder = new FlatBufferBuilder(50);

        int controllerStateOffset = rlbot.flat.ControllerState.createControllerState(
                builder,
                controllerState.getThrottle(),
                controllerState.getSteer(),
                controllerState.getPitch(),
                controllerState.getYaw(),
                controllerState.getRoll(),
                controllerState.holdJump(),
                controllerState.holdBoost(),
                controllerState.holdHandbrake());

        int playerInputOffset = rlbot.flat.PlayerInput.createPlayerInput(
                builder,
                index,
                controllerStateOffset);

        builder.finish(playerInputOffset);

        final byte[] protoBytes = builder.sizedByteArray();
        final Memory memory = getMemory(protoBytes);
        UpdatePlayerInputFlatbuffer(memory, protoBytes.length);
    }

    /**
     * Set player input in protobuf format.
     */
    public static void setPlayerInputProtobuf(ControllerState controllerState, int index) {

        GameData.PlayerInput playerInput = GameData.PlayerInput.newBuilder()
                .setPlayerIndex(index)
                .setControllerState(GameData.ControllerState.newBuilder()
                        .setThrottle(controllerState.getThrottle())
                        .setSteer(controllerState.getSteer())
                        .setPitch(controllerState.getPitch())
                        .setYaw(controllerState.getYaw())
                        .setRoll(controllerState.getRoll())
                        .setBoost(controllerState.holdBoost())
                        .setHandbrake(controllerState.holdHandbrake())
                        .setJump(controllerState.holdJump())
                        .build())
                .build();

        final byte[] protoBytes = playerInput.toByteArray();
        final Memory memory = getMemory(protoBytes);
        UpdatePlayerInputProto(memory, protoBytes.length);
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
