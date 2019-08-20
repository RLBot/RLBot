package rlbot.cppinterop;

import com.google.flatbuffers.FlatBufferBuilder;
import com.sun.jna.Memory;
import com.sun.jna.Native;
import com.sun.jna.Pointer;
import rlbot.ControllerState;
import rlbot.flat.*;
import rlbot.gamestate.GameStatePacket;
import rlbot.render.RenderPacket;

import java.io.File;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

/**
 * This is the main communication gateway between Java and Rocket League.
 * It contains methods for retrieving data, sending car controls, rendering graphics, etc.
 *
 * It does so via the "interface dll" which is vended in the rlbot python package at
 * https://pypi.org/project/rlbot/ and authored at https://github.com/RLBot/RLBot
 */
public class RLBotDll {

    // Java bots must either add this in their classpath, or specify the jna.library.path JVM arg.
    private static final String LOCAL_DLL_DIR = "build/dll";
    private static final String DLL_NAME_SANS_EXTENSION = "RLBot_Core_Interface";
    private static final String DLL_NAME_SANS_EXTENSION_32 = "RLBot_Core_Interface_32";

    private static native ByteBufferStruct UpdateLiveDataPacketFlatbuffer();
    private static native int UpdatePlayerInputFlatbuffer(Pointer ptr, int size);
    private static native ByteBufferStruct UpdateFieldInfoFlatbuffer();
    private static native int RenderGroup(Pointer ptr, int size);
    private static native int SetGameState(Pointer ptr, int size);
    private static native ByteBufferStruct GetBallPrediction();
    private static native int SendQuickChat(Pointer ptr, int size);
    private static native ByteBufferStruct ReceiveChat(int botIndex, int teamIndex, int lastMessageIndex);
    private static native int StartMatchFlatbuffer(Pointer ptr, int size);
    private static native ByteBufferStruct GetMatchSettings();
    private static native boolean IsInitialized();  // This asks the dll instance whether it is done initializing.
    private static native void Free(Pointer ptr);

    // This helps us keep track internally of whether we have initialized, so that we only do it once.
    private static boolean isInitializationComplete = false;
    private static final Object fileLock = new Object();

    public static void initialize(final String interfaceDllPath) throws IOException {
        synchronized(fileLock) {
            if (isInitializationComplete) {
                return;
            }

            // https://www.quora.com/How-do-you-know-if-youre-running-Java-in-32-bits-or-64-bits
            boolean is64Bit = System.getProperty("os.arch").contains("64");
            System.out.println("Detected " + (is64Bit ? "64" : "32") + "bit JVM.");

            final String dllNameSansExtension = is64Bit ? DLL_NAME_SANS_EXTENSION : DLL_NAME_SANS_EXTENSION_32;

            final File directory = getDllDirectory();

            if (!directory.exists()) {
                directory.mkdirs();
            }

            String dllName = dllNameSansExtension + ".dll";

            // Currently interfaceDllPath points to a 64 or 32 bit dll based on the bitness
            // of the python installation. That's not what we want, we care about the
            // bitness of the JVM, so pick the correct one from the folder.

            final Path givenPath = Paths.get(interfaceDllPath);
            final Path dllFolder;
            if (Files.isDirectory(givenPath)) {
                dllFolder = givenPath;
            } else {
                dllFolder = givenPath.getParent();
            }
            Path dllSource = dllFolder.resolve(dllName);

            // Copy the interface dll to a known location that is already on the classpath.
            Files.copy(
                    dllSource,
                    Paths.get(directory.toString(), dllName),
                    StandardCopyOption.REPLACE_EXISTING);

            System.out.println("Loading DLL from " + dllSource);
            Native.register(dllNameSansExtension);

            int attemptCount = 0;
            while (!IsInitialized()) {
                try {
                    attemptCount++;
                    if (attemptCount > 100) {
                        // Should throw after about 10 seconds of waiting.
                        throw new RLBotInterfaceException("The RLBot interface appears to be taking forever to initialize!");
                    }
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }

            isInitializationComplete = true;
        }
    }

    private static File getDllDirectory() throws IOException {
        final String jnaPath = System.getProperty("jna.library.path");
        if (jnaPath == null) {
            return new File(LOCAL_DLL_DIR).getCanonicalFile();
        }
        return new File(jnaPath).getCanonicalFile();
    }

    /**
     * Retrieves up-to-date game information like the positions of the ball and cars, among many other things.
     */
    public static GameTickPacket getFlatbufferPacket() throws RLBotInterfaceException {
        try {
            final ByteBufferStruct struct = UpdateLiveDataPacketFlatbuffer();
            if (struct.size < 4) {
                throw new RLBotInterfaceException("Flatbuffer packet is too small, match is probably not running!");
            }
            final byte[] protoBytes = struct.ptr.getByteArray(0, struct.size);
            Free(struct.ptr);
            return GameTickPacket.getRootAsGameTickPacket(ByteBuffer.wrap(protoBytes));
        } catch (final UnsatisfiedLinkError error) {
            throw new RLBotInterfaceException("Could not find interface dll! Did initialize get called?", error);
        } catch (final Error error) {
            throw new RLBotInterfaceException(error);
        }
    }

    /**
     * Retrieves information about boost pad locations, goal locations, dropshot tile locations, etc.
     */
    public static FieldInfo getFieldInfo() throws RLBotInterfaceException {
        try {
            final ByteBufferStruct struct = UpdateFieldInfoFlatbuffer();
            if (struct.size < 4) {
                throw new RLBotInterfaceException("Flatbuffer packet is too small, match is probably not running!");
            }
            final byte[] protoBytes = struct.ptr.getByteArray(0, struct.size);
            Free(struct.ptr);
            return FieldInfo.getRootAsFieldInfo(ByteBuffer.wrap(protoBytes));
        } catch (final UnsatisfiedLinkError error) {
            throw new RLBotInterfaceException("Could not find interface dll! Did initialize get called?", error);
        } catch (final Error error) {
            throw new RLBotInterfaceException(error);
        }
    }

    /**
     * Set player input in flatbuffer format.
     */
    public static void setPlayerInputFlatbuffer(ControllerState controllerState, int index) {

        FlatBufferBuilder builder = new FlatBufferBuilder(50);

        rlbot.flat.ControllerState.startControllerState(builder);

        rlbot.flat.ControllerState.addBoost(builder, controllerState.holdBoost());
        rlbot.flat.ControllerState.addThrottle(builder, controllerState.getThrottle());
        rlbot.flat.ControllerState.addSteer(builder, controllerState.getSteer());
        rlbot.flat.ControllerState.addPitch(builder, controllerState.getPitch());
        rlbot.flat.ControllerState.addYaw(builder, controllerState.getYaw());
        rlbot.flat.ControllerState.addRoll(builder, controllerState.getRoll());
        rlbot.flat.ControllerState.addJump(builder, controllerState.holdJump());
        rlbot.flat.ControllerState.addBoost(builder, controllerState.holdBoost());
        rlbot.flat.ControllerState.addHandbrake(builder, controllerState.holdHandbrake());
        rlbot.flat.ControllerState.addUseItem(builder, controllerState.holdUseItem());

        int controllerStateOffset = rlbot.flat.ControllerState.endControllerState(builder);

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
    public static BallPrediction getBallPrediction() throws RLBotInterfaceException {
        try {
            final ByteBufferStruct struct = GetBallPrediction();
            if (struct.size < 4) {
                throw new RLBotInterfaceException("Flatbuffer packet is too small, match is probably not running!");
            }
            final byte[] protoBytes = struct.ptr.getByteArray(0, struct.size);
            Free(struct.ptr);
            return BallPrediction.getRootAsBallPrediction(ByteBuffer.wrap(protoBytes));
        } catch (final UnsatisfiedLinkError error) {
            throw new RLBotInterfaceException("Could not find interface dll! Did initialize get called?", error);
        } catch (final Error error) {
            throw new RLBotInterfaceException(error);
        }
    }

    /**
     * Sends a quick chat message to the game. If you send too many too fast, you may receive a {@link RLBotCoreStatus}
     * of QuickChatRateExceeded, which means your attempt at quick chat was ignored.
     *
     * Example usage:
     * sendQuickChat(this.playerIndex, false, QuickChatSelection.Information_IGotIt);
     *
     * @param playerIndex the index of the player who is sending the quick chat.
     * @param teamOnly whether this chat's visibility should be restricted to the player's team. Note: this is
     *                 currently meaningless because we don't support receiving quickchat yet. It's write-only,
     *                 a bit like the rendering feature.
     * @param quickChatSelection The quick chat to send. Use the constants in {@link QuickChatSelection}.
     */
    public static RLBotCoreStatus sendQuickChat(int playerIndex, boolean teamOnly, byte quickChatSelection) {
        FlatBufferBuilder builder = new FlatBufferBuilder(50);

        QuickChat.startQuickChat(builder);
        QuickChat.addQuickChatSelection(builder, quickChatSelection);
        QuickChat.addPlayerIndex(builder, playerIndex);
        QuickChat.addTeamOnly(builder, teamOnly);
        int offset = QuickChat.endQuickChat(builder);

        builder.finish(offset);

        final byte[] protoBytes = builder.sizedByteArray();
        final Memory memory = getMemory(protoBytes);
        return RLBotCoreStatus.fromDllResult(SendQuickChat(memory, protoBytes.length));
    }

    /**
     * Reads quickchat that has been sent by other bots.
     * @param botIndex Please pass the bot's own index so that its own messages aren't returned.
     * @param teamIndex Pass the bot's team so that the other team's private team chat is not returned.
     * @param lastMessageIndex Each message has an index inside it. The first time you use this function,
     *                         you can pass -1. On subsequent calls, you should pass the index that was
     *                         inside the most recent message so that you don't receive any of the messages
     *                         twice.
     */
    public static QuickChatMessages receiveQuickChat(int botIndex, int teamIndex, int lastMessageIndex) throws RLBotInterfaceException {
        try {
            final ByteBufferStruct byteBuffer = ReceiveChat(botIndex, teamIndex, lastMessageIndex);
            if (byteBuffer.size < 4) {
                throw new RLBotInterfaceException("Flatbuffer packet is too small, quick chat is probably not available!");
            }
            final byte[] protoBytes = byteBuffer.ptr.getByteArray(0, byteBuffer.size);
            Free(byteBuffer.ptr);
            return QuickChatMessages.getRootAsQuickChatMessages(ByteBuffer.wrap(protoBytes));
        } catch (final UnsatisfiedLinkError error) {
            throw new RLBotInterfaceException("Could not find interface dll! Did initialize get called?", error);
        } catch (final Error error) {
            throw new RLBotInterfaceException(error);
        }
    }

    /**
     * Starts a match inside RocketLeague with the specified settings.
     *
     * Usage:
     * FlatBufferBuilder builder = new FlatBufferBuilder();
     * int offset = MatchSettings.createMatchSettings(builder, ...);
     * builder.finish(offset);
     * startMatch(builder);
     *
     * @param matchSettingsBuilder a FlatBufferBuilder holding a MatchSettings object which has been fully populated and finished.
     * @return A status indicating the validation result of the match settings.
     */
    public static RLBotCoreStatus startMatch(final FlatBufferBuilder matchSettingsBuilder) {

        final byte[] bytes = matchSettingsBuilder.sizedByteArray();
        final Memory memory = getMemory(bytes);
        return RLBotCoreStatus.fromDllResult(StartMatchFlatbuffer(memory, bytes.length));
    }

    /**
     * Gets the most recent match settings that were sent to RLBot. Useful for determining the game mode,
     * what map we're playing on, mutators, etc.
     */
    public static MatchSettings getMatchSettings() throws RLBotInterfaceException {
        try {
            final ByteBufferStruct struct = GetMatchSettings();
            if (struct.size < 4) {
                throw new RLBotInterfaceException("Flatbuffer packet is too small, match settings are probably not present!");
            }
            final byte[] protoBytes = struct.ptr.getByteArray(0, struct.size);
            Free(struct.ptr);
            return MatchSettings.getRootAsMatchSettings(ByteBuffer.wrap(protoBytes));
        } catch (final UnsatisfiedLinkError error) {
            throw new RLBotInterfaceException("Could not find interface dll! Did initialize get called?", error);
        } catch (final Error error) {
            throw new RLBotInterfaceException(error);
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
