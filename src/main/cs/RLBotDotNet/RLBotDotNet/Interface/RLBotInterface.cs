using System;
using rlbot.flat;
using FlatBuffers;
using System.Runtime.InteropServices;

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
        private const string InterfaceDllPath = "dll/RLBot_Core_Interface.dll";
#else
        private const string InterfaceDllPath = "dll/RLBot_Core_Interface_32.dll";
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
        #endregion

        /// <summary>
        /// Returns the current frame's GameTickPacket.
        /// </summary>
        /// <returns>The current frame's GameTickPacket.</returns>
        public static GameTickPacket GetGameTickPacket()
        {
            ByteBufferStruct byteBuffer = UpdateLiveDataPacketFlatbuffer();
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
    }
}
