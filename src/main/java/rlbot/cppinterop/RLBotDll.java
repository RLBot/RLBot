package rlbot.cppinterop;

import com.google.flatbuffers.FlatBufferBuilder;
import com.sun.jna.Memory;
import com.sun.jna.Native;
import com.sun.jna.Pointer;
import rlbot.ControllerState;
import rlbot.flat.BallPrediction;
import rlbot.flat.FieldInfo;
import rlbot.flat.GameTickPacket;
import rlbot.gamestate.GameStatePacket;
import rlbot.render.RenderPacket;

import java.io.File;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

public class RLBotDll {

    // Java bots must either add this in their classpath, or specify the jna.library.path JVM arg.
    private static final String LOCAL_DLL_DIR = "build/dll";
    private static final String DLL_NAME_SANS_EXTENSION = "RLBot_Core_Interface";

    private static native ByteBufferStruct UpdateLiveDataPacketFlatbuffer();
    private static native int UpdatePlayerInputFlatbuffer(Pointer ptr, int size);
    private static native ByteBufferStruct UpdateFieldInfoFlatbuffer();
    private static native int RenderGroup(Pointer ptr, int size);
    private static native int SetGameState(Pointer ptr, int size);
    private static native ByteBufferStruct GetBallPrediction();

    private static boolean isInitialized = false;
    private static final Object fileLock = new Object();

    public static void initialize(final String interfaceDllPath) throws IOException {
        synchronized(fileLock) {
            if (isInitialized) {
                return;
            }

            final File directory = getDllDirectory();

            if (!directory.exists()) {
                directory.mkdirs();
            }

            // Copy the interface dll to a known location that is already on the classpath.
            Files.copy(
                    Paths.get(interfaceDllPath),
                    Paths.get(directory.toString(), DLL_NAME_SANS_EXTENSION + ".dll"),
                    StandardCopyOption.REPLACE_EXISTING);

            Native.register(DLL_NAME_SANS_EXTENSION);

            isInitialized = true;
        }
    }

    private static File getDllDirectory() {
        final String jnaPath = System.getProperty("jna.library.path");
        if (jnaPath == null) {
            return new File(LOCAL_DLL_DIR);
        }
        return new File(jnaPath);
    }

    /**
     * Retrieves up-to-date game information like the positions of the ball and cars, among many other things.
     */
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

    /**
     * Retrieves information about boost pad locations, goal locations, dropshot tile locations, etc.
     */
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

    /**
     * Modifies the position, velocity, etc of the ball and cars, according to the contents of the gameStatePacket.
     * See https://github.com/RLBot/RLBotJavaExample/wiki/Manipulating-Game-State for detailed documentation.
     */
    public static void setGameState(final GameStatePacket gameStatePacket) {
        byte[] bytes = gameStatePacket.getBytes();
        final Memory memory = getMemory(bytes);
        SetGameState(memory, bytes.length);
    }

    /**
     * Gets the predicted path of the ball as a list of slices.
     * See https://github.com/RLBot/RLBotJavaExample/wiki/Ball-Path-Prediction for more details.
     */
    public static BallPrediction getBallPrediction() throws IOException {
        try {
            final ByteBufferStruct struct = GetBallPrediction();
            if (struct.size < 4) {
                throw new IOException("Flatbuffer packet is too small, match is probably not running!");
            }
            final byte[] protoBytes = struct.ptr.getByteArray(0, struct.size);
            return BallPrediction.getRootAsBallPrediction(ByteBuffer.wrap(protoBytes));
        } catch (final UnsatisfiedLinkError error) {
            throw new IOException("Could not find interface dll! Did initialize get called?", error);
        } catch (final Error error) {
            throw new IOException(error);
        }
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
