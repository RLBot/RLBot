package rlbot.cppinterop;

import com.google.flatbuffers.FlatBufferBuilder;
import com.sun.jna.Memory;
import com.sun.jna.Native;
import com.sun.jna.Pointer;
import rlbot.ControllerState;
import rlbot.flat.FieldInfo;
import rlbot.flat.GameTickPacket;
import rlbot.render.RenderPacket;

import java.io.File;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

public class RLBotDll {

    private static final String LOCAL_DLL_DIR = "build/dll";  // Java bots must this in their classpath
    private static final String DLL_NAME_SANS_EXTENSION = "RLBot_Core_Interface";

    private static native ByteBufferStruct UpdateLiveDataPacketFlatbuffer();
    private static native int UpdatePlayerInputFlatbuffer(Pointer ptr, int size);
    private static native ByteBufferStruct UpdateFieldInfoFlatbuffer();
    private static native int RenderGroup(Pointer ptr, int size);

    private static boolean isInitialized = false;
    private static Object fileLock = new Object();

    public static void initialize(final String interfaceDllPath) throws IOException {
        synchronized(fileLock) {
            if (isInitialized) {
                return;
            }

            File directory = new File(LOCAL_DLL_DIR);
            if (!directory.exists()) {
                directory.mkdirs();
            }

            // Copy the interface dll to a known location that is already on the classpath.
            Files.copy(
                    Paths.get(interfaceDllPath),
                    Paths.get( LOCAL_DLL_DIR, DLL_NAME_SANS_EXTENSION + ".dll"),
                    StandardCopyOption.REPLACE_EXISTING);

            Native.register(DLL_NAME_SANS_EXTENSION);

            isInitialized = true;
        }
    }

    public static GameTickPacket getFlatbufferPacket() throws IOException {
        try {
            final ByteBufferStruct struct = UpdateLiveDataPacketFlatbuffer();
            if (struct.size < 4) {
                throw new IOException("Flatbuffer packet is too small, match is probably not running!");
            }
            final byte[] protoBytes = struct.ptr.getByteArray(0, struct.size);
            return GameTickPacket.getRootAsGameTickPacket(ByteBuffer.wrap(protoBytes));
        } catch (final UnsatisfiedLinkError error) {
            throw new IOException("Could not find interface dll! Did initialize get called?", error);
        } catch (final Error error) {
            throw new IOException(error);
        }
    }

    public static FieldInfo getFieldInfo() throws IOException {
        try {
            final ByteBufferStruct struct = UpdateFieldInfoFlatbuffer();
            if (struct.size < 4) {
                throw new IOException("Flatbuffer packet is too small, match is probably not running!");
            }
            final byte[] protoBytes = struct.ptr.getByteArray(0, struct.size);
            return FieldInfo.getRootAsFieldInfo(ByteBuffer.wrap(protoBytes));
        } catch (final UnsatisfiedLinkError error) {
            throw new IOException("Could not find interface dll! Did initialize get called?", error);
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
     * Send a render packet to the game to be displayed on screen.
     * It will remain there until replaced or erased.
     */
    public static void sendRenderPacket(final RenderPacket finishedRender) {

        byte[] bytes = finishedRender.getBytes();
        final Memory memory = getMemory(bytes);
        RenderGroup(memory, bytes.length);
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
