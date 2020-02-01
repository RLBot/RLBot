using System;
using rlbot.flat;
using FlatBuffers;
using System.Runtime.InteropServices;
using RLBotDotNet.Renderer;
using RLBotDotNet.GameState;

namespace RLBotDotNet.Utils
{
    /// <summary>
    /// Contains all the methods provided by the interface DLL.
    /// </summary>
    public static class RLBotInterface
    {
        public const string InterfaceDllPath = "dll/RLBot_Core_Interface.dll";

        #region DllImports

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        [return: MarshalAs(UnmanagedType.I1)]
        public extern static bool IsInitialized();

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static ByteBufferStruct UpdateLiveDataPacketFlatbuffer();

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static ByteBufferStruct FreshLiveDataPacketFlatbuffer(int timeoutMillis, int key);

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static ByteBufferStruct UpdateRigidBodyTickFlatbuffer();

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static ByteBufferStruct UpdateFieldInfoFlatbuffer();

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static ByteBufferStruct GetBallPrediction();

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static int UpdatePlayerInputFlatbuffer(byte[] bytes, int size);

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static int SendQuickChat(byte[] quickChatMessage, int protoSize);

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static ByteBufferStruct ReceiveChat(int botIndex, int teamIndex, int lastMessageIndex);

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static int RenderGroup(byte[] renderGroup, int protoSize);

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static void Free(IntPtr ptr);

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static int SetGameState(byte[] bytes, int size);

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static ByteBufferStruct GetMatchSettings();

        #endregion

        /// <summary>
        /// Returns the current frame's GameTickPacket.
        /// </summary>
        /// <returns>The current frame's GameTickPacket.</returns>
        public static GameTickPacket GetGameTickPacket()
        {
            ByteBufferStruct byteBuffer = UpdateLiveDataPacketFlatbuffer();
            if (byteBuffer.size < 4)
                throw new FlatbuffersPacketException("Flatbuffers packet is too small. Match is probably not running!");

            byte[] bufferBytes = new byte[byteBuffer.size];
            Marshal.Copy(byteBuffer.ptr, bufferBytes, 0, byteBuffer.size);
            Free(byteBuffer.ptr);

            return GameTickPacket.GetRootAsGameTickPacket(new ByteBuffer(bufferBytes));
        }

        public static GameTickPacket WaitForFreshPacket(int timeoutMillis, int key)
        {
            ByteBufferStruct byteBuffer = FreshLiveDataPacketFlatbuffer(timeoutMillis, key);
            if (byteBuffer.size < 4)
                throw new FlatbuffersPacketException("Flatbuffers packet is too small. Match is probably not running!");

            byte[] bufferBytes = new byte[byteBuffer.size];
            Marshal.Copy(byteBuffer.ptr, bufferBytes, 0, byteBuffer.size);
            Free(byteBuffer.ptr);

            return GameTickPacket.GetRootAsGameTickPacket(new ByteBuffer(bufferBytes));
        }

        /// <summary>
        /// Returns the current frame's RigidBodyTick.
        /// </summary>
        /// <returns>The current frame's RigidBodyTick.</returns>
        public static RigidBodyTick GetRigidBodyTick()
        {
            ByteBufferStruct byteBuffer = UpdateRigidBodyTickFlatbuffer();
            if (byteBuffer.size < 4)
                throw new FlatbuffersPacketException("Flatbuffers packet is too small. Match is probably not running!");

            byte[] bufferBytes = new byte[byteBuffer.size];
            Marshal.Copy(byteBuffer.ptr, bufferBytes, 0, byteBuffer.size);
            Free(byteBuffer.ptr);

            return RigidBodyTick.GetRootAsRigidBodyTick(new ByteBuffer(bufferBytes));
        }

        /// <summary>
        /// Returns the game's FieldInfo.
        /// </summary>
        /// <returns>The game's FieldInfo.</returns>
        public static FieldInfo GetFieldInfo()
        {
            ByteBufferStruct byteBuffer = UpdateFieldInfoFlatbuffer();
            if (byteBuffer.size < 4)
                throw new FlatbuffersPacketException("Flatbuffers packet is too small. Match is probably not running!");

            byte[] bufferBytes = new byte[byteBuffer.size];
            Marshal.Copy(byteBuffer.ptr, bufferBytes, 0, byteBuffer.size);
            Free(byteBuffer.ptr);

            return FieldInfo.GetRootAsFieldInfo(new ByteBuffer(bufferBytes));
        }

        /// <summary>
        /// Returns 6 seconds of the ball physics prediction.
        /// </summary>
        /// <returns>6 seconds of the ball physics prediction.</returns>
        public static BallPrediction GetBallPredictionData()
        {
            ByteBufferStruct byteBuffer = GetBallPrediction();
            if (byteBuffer.size < 4)
                throw new FlatbuffersPacketException("Flatbuffers packet is too small. Match is probably not running!");

            byte[] bufferBytes = new byte[byteBuffer.size];
            Marshal.Copy(byteBuffer.ptr, bufferBytes, 0, byteBuffer.size);
            Free(byteBuffer.ptr);

            return BallPrediction.GetRootAsBallPrediction(new ByteBuffer(bufferBytes));
        }


        /// <summary>
        /// Sets the bot's controller inputs.
        /// </summary>
        /// <param name="controller">The controller to set the inputs to.</param>
        /// <param name="index">The index of the bot's car.</param>
        public static void SetBotInput(Controller controller, int index)
        {
            FlatBufferBuilder builder = new FlatBufferBuilder(50);

            Offset<ControllerState> controllerStateOffset = ControllerState.CreateControllerState(
                builder,
                controller.Throttle,
                controller.Steer,
                controller.Pitch,
                controller.Yaw,
                controller.Roll,
                controller.Jump,
                controller.Boost,
                controller.Handbrake,
                controller.UseItem);

            Offset<PlayerInput> playerInputOffset = PlayerInput.CreatePlayerInput(
                builder,
                index,
                controllerStateOffset);

            builder.Finish(playerInputOffset.Value);
            byte[] bufferBytes = builder.SizedByteArray();
            int status = UpdatePlayerInputFlatbuffer(bufferBytes, bufferBytes.Length);

            if (status > 0)
                throw NewRLBotCoreException((RLBotCoreStatus) status);
        }


        /// <summary>
        /// Sends a quick chat flat message.
        /// </summary>
        /// <param name="playerIndex">The index of the bot's car.</param>
        /// <param name="teamOnly">Flag indicating whether the quick chat message is for the player's team only or not.</param>
        /// <param name="quickChat">The quick chat selection to send.</param>
        public static void SendQuickChatFlat(int playerIndex, bool teamOnly, QuickChatSelection quickChat)
        {
            FlatBufferBuilder builder = new FlatBufferBuilder(50);

            var offset = QuickChat.CreateQuickChat(
                builder,
                quickChat,
                playerIndex,
                teamOnly);

            builder.Finish(offset.Value);
            byte[] bufferBytes = builder.SizedByteArray();
            int status = SendQuickChat(bufferBytes, bufferBytes.Length);

            if (status > 0)
                throw NewRLBotCoreException((RLBotCoreStatus) status);
        }

        /// <summary>
        /// Gets a list of chat messages.
        /// </summary>
        /// <param name="botIndex">Index of the receiving bot.</param>
        /// <param name="teamIndex">Team index of the receiving bot.</param>
        /// <param name="lastMessageIndex">Message index of the last received message.</param>
        /// <returns>List of new messages.</returns>
        public static QuickChatMessages ReceiveQuickChat(int botIndex, int teamIndex, int lastMessageIndex)
        {
            ByteBufferStruct byteBuffer = ReceiveChat(botIndex, teamIndex, lastMessageIndex);
            if (byteBuffer.size < 4)
                throw new FlatbuffersPacketException("Flatbuffers packet is too small. Match is probably not running!");

            byte[] bufferBytes = new byte[byteBuffer.size];
            Marshal.Copy(byteBuffer.ptr, bufferBytes, 0, byteBuffer.size);
            Free(byteBuffer.ptr);

            return QuickChatMessages.GetRootAsQuickChatMessages(new ByteBuffer(bufferBytes));
        }

        /// <summary>
        /// Sets the current state of the game.
        /// </summary>
        /// <param name="gameState">The desired state.</param>
        public static void SetGameStatePacket(GameStatePacket gameState)
        {
            byte[] data = gameState.Data;
            int status = SetGameState(data, data.Length);

            if (status > 0)
                throw NewRLBotCoreException((RLBotCoreStatus) status);
        }

        /// <summary>
        /// Renders a render packet to the screen.
        /// </summary>
        /// <param name="finishedRender">The render packet to render.</param>
        public static void RenderPacket(RenderPacket finishedRender)
        {
            byte[] bytes = finishedRender.Bytes;
            int status = RenderGroup(bytes, bytes.Length);

            if (status > 0)
                throw NewRLBotCoreException((RLBotCoreStatus) status);
        }

        /// <summary>
        /// Returns the match settings that were most recently sent to RLBot.
        /// Useful for determining the game mode, what map we're playing on, mutators, etc.
        /// </summary>
        /// <returns>The MatchSettings object, as defined in the flatbuffer spec.</returns>
        public static MatchSettings GetMatchSettingsData()
        {
            ByteBufferStruct byteBuffer = GetMatchSettings();
            if (byteBuffer.size < 4)
                throw new FlatbuffersPacketException("Flatbuffers packet is too small. Match settings are probably not available!");

            byte[] bufferBytes = new byte[byteBuffer.size];
            Marshal.Copy(byteBuffer.ptr, bufferBytes, 0, byteBuffer.size);
            Free(byteBuffer.ptr);

            return MatchSettings.GetRootAsMatchSettings(new ByteBuffer(bufferBytes));
        }

        private static RLBotCoreException NewRLBotCoreException(RLBotCoreStatus status)
        {
            // Possible to add more code here to make the exception messages more verbose.
            return new RLBotCoreException(status.ToString());
        }
    }
}