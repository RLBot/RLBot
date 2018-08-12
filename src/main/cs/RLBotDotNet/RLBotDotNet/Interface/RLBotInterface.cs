using System;
using rlbot.flat;
using FlatBuffers;
using System.Runtime.InteropServices;
using RLBotDotNet.Renderer;

namespace RLBotDotNet.Utils
{
    /// <summary>
    /// Contains all the methods provided by the interface DLL.
    /// </summary>
    public static class RLBotInterface
    {
        // The folder containing the bot runner executable MUST contain a dll folder containing the interface DLLs.
        // There is a 32 bit version and a 64 bit version of the interface.
        // We want to use the right one depending on the RLBotDotNet build.
#if (X64)
        public const string InterfaceDllPath = "dll/RLBot_Core_Interface.dll";
#else
        public const string InterfaceDllPath = "dll/RLBot_Core_Interface_32.dll";
#endif

        #region DllImports
        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static bool IsInitialized();

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static ByteBufferStruct UpdateLiveDataPacketFlatbuffer();

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static ByteBufferStruct UpdateFieldInfoFlatbuffer();

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static int UpdatePlayerInputFlatbuffer(byte[] bytes, int size);

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static int SendQuickChat(byte[] quickChatMessage, int protoSize);

        [DllImport(InterfaceDllPath, CallingConvention = CallingConvention.Cdecl)]
        public extern static int RenderGroup(byte[] renderGroup, int protoSize);
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

            return GameTickPacket.GetRootAsGameTickPacket(new ByteBuffer(bufferBytes));
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

            return FieldInfo.GetRootAsFieldInfo(new ByteBuffer(bufferBytes));
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
                controller.Handbrake);

            Offset<PlayerInput> playerInputOffset = PlayerInput.CreatePlayerInput(
                builder,
                index,
                controllerStateOffset);

            builder.Finish(playerInputOffset.Value);
            byte[] bufferBytes = builder.SizedByteArray();
            UpdatePlayerInputFlatbuffer(bufferBytes, bufferBytes.Length);
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
            SendQuickChat(bufferBytes, bufferBytes.Length);
        }

        /// <summary>
        /// Renders a render packet to the screen.
        /// </summary>
        /// <param name="finishedRender">The render packet to render.</param>
        public static void RenderPacket(RenderPacket finishedRender)
        {
            byte[] bytes = finishedRender.Bytes;
            RenderGroup(bytes, bytes.Length);
        }
    }
}
