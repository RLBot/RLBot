#include <thread>
#include <DebugHelper.hpp>

#include "GamePacket.hpp"
#include "GameFunctions/GameFunctions.hpp"
#include <MessageTranslation/FlatbufferTranslator.hpp>
#include <MessageTranslation/StructToRLBotFlatbuffer.hpp>
#include <MutexUtilities/SafeFlatbufferHolder.hpp>
#include <map>

namespace GameFunctions
{

	static std::map<int, char> frame_counts;

	//////////////
	// FIELD INFO
	//////////////

	static SafeFlatbufferHolder field_info_packet_flatbuffer_tcp;

	void setFieldInfoPacketFlatbuffer(std::string flatbuffer_content) {
		field_info_packet_flatbuffer_tcp.set(flatbuffer_content);
	}

	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoFlatbuffer()
	{
		return field_info_packet_flatbuffer_tcp.copyOut();
	}

	// Ctypes
	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateFieldInfo(FieldInfo* pFieldInfo)
	{
		ByteBuffer fieldInfo = UpdateFieldInfoFlatbuffer();
		FlatbufferTranslator::translateToFieldInfoStruct(fieldInfo, pFieldInfo);
		delete[] fieldInfo.ptr;

		return RLBotCoreStatus::Success;
	}

	//////////////
	// GAME PACKET
	//////////////

	static SafeFlatbufferHolder game_tick_packet_flatbuffer_tcp;
	static char frame_count = 0;

	void setGameTickPacketFlatbuffer(std::string flatbuffer_content) {
		game_tick_packet_flatbuffer_tcp.set(flatbuffer_content);
		frame_count++;
	}

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketFlatbuffer()
	{
		if (!GameFunctions::tcpConnected.load()) {
			// This is here for backwards compatibility. Ideally, people should be calling StartTcpCommunication directly on the dll.
			// However, there are many bots written in Java, C#, etc that are already compiled and which don't do that.
			// We're doing this check here to create binary compatibility with those bots, because they ALL
			// call UpdateLiveDataPacketFlatbuffer, either directly or indirectly.
			// We can't start TCP communication on DLL load because it spawns a thread and that's not allowed.
			// The port here is the default RLBot.exe port (23233 as defined in python) plus 1 (matching the computation in Main.cpp).
			// This could easily go badly, so bots are highly encouraged to not rely on this compatibility shim.
			printf("WARNING: Your bot should be calling StartTcpCommunication on the DLL but it's not! Please update to the latest library version, or it might break sometimes.\n");
			GameFunctions::StartTcpCommunication(23234);
		}

		return game_tick_packet_flatbuffer_tcp.copyOut();
	}

	// Ctypes
	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateLiveDataPacket(LiveDataPacket* pLiveData)
	{
		ByteBuffer flatbuffer = UpdateLiveDataPacketFlatbuffer();
		FlatbufferTranslator::translateToStruct(flatbuffer, pLiveData);
		delete[] flatbuffer.ptr;

		return RLBotCoreStatus::Success;
	}

	///////////////
	// PHYSICS TICK
	///////////////

	extern "C" ByteBuffer RLBOT_CORE_API UpdateRigidBodyTickFlatbuffer()
	{
		// Rigid body tick is on a deprecation path. Here we are taking inefficient steps
		// to transform it into flatbuffer format to provide legacy support.

		RigidBodyTick tick;
		UpdateRigidBodyTick(&tick);
		flatbuffers::FlatBufferBuilder builder;
		StructToRLBotFlatbuffer::FillRigidBody(&builder, tick);

		unsigned char *buffer = new unsigned char[builder.GetSize()];
		memcpy(buffer, builder.GetBufferPointer(), builder.GetSize());

		ByteBuffer buf;
		buf.size = builder.GetSize();
		buf.ptr = buffer;
		return buf;
	}

	void fillQuaternion(PyStruct::Rotator rot, Quaternion* quat)
	{
		// Yaw, pitch, and roll are in radians.
		float yaw = rot.yaw;
		float pitch = rot.pitch;
		float roll = rot.roll;

		// Pulled from https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#Source_Code
		double cy = cos(yaw * 0.5);
		double sy = sin(yaw * 0.5);
		double cp = cos(pitch * 0.5);
		double sp = sin(pitch * 0.5);
		double cr = cos(roll * 0.5);
		double sr = sin(roll * 0.5);

		quat->x = cy * cp * sr - sy * sp * cr;
		quat->y = sy * cp * sr + cy * sp * cr;
		quat->z = sy * cp * cr - cy * sp * sr;
		quat->w = cy * cp * cr + sy * sp * sr;
	}


	void copyPhysicsToRigidBodyState(Physics* physics, RigidBodyState* rbState, int frameNum) {
		rbState->angularVelocity = physics->angularVelocity;
		rbState->location = physics->location;
		rbState->velocity = physics->velocity;
		fillQuaternion(physics->rotation, &rbState->rotation);
		rbState->frame = frameNum;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateRigidBodyTick(RigidBodyTick* rigidBodyTick)
	{
		LiveDataPacket normal_packet;
		UpdateLiveDataPacket(&normal_packet);

		rigidBodyTick->numPlayers = normal_packet.numCars;
		for (int i = 0; i < normal_packet.numCars; i++) {
			copyPhysicsToRigidBodyState(&normal_packet.gameCars[i].physics, &rigidBodyTick->players[i].state, normal_packet.gameInfo.frameNum);
		}

		copyPhysicsToRigidBodyState(&normal_packet.gameBall.physics, &rigidBodyTick->ball.state, normal_packet.gameInfo.frameNum);

		return RLBotCoreStatus::Success;
	}

	static SafeFlatbufferHolder match_settings_flatbuffer_tcp;

	void setMatchSettingsFlatbuffer(std::string flatbuffer_content) {
		match_settings_flatbuffer_tcp.set(flatbuffer_content);
	}

	extern "C" DLL_EXPORT ByteBuffer RLBOT_CORE_API GetMatchSettings()
	{
		return match_settings_flatbuffer_tcp.copyOut();
	}

	///////////////
	// FRESH PACKETS
	///////////////

	// On windows it is probably not possible to sleep for only 500 microseconds, and it seems like
	// we are effectively being rounded up to the minimum resolution here:
	// https://docs.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timebeginperiod
	// We have set the minimum resolution to 1ms on DLL init to minimize this problem.
	// Keeping this at 500 microseconds anyway for the sake of Linux.
	static const int sleep_microseconds = 500;

	void waitForFrame(int timeoutMillis, int key)
	{
		auto start = std::chrono::system_clock::now();

		// The for loop is not strictly necessary because we'll generally break sooner due to
		// the system clock registering the timeout. Still using the for loop rather than a
		// while(true) out of an abundance of caution.
		for (int i = 0; i < timeoutMillis * 1000 / sleep_microseconds; i++) {
			int frameCount = frame_count;
			if (frameCount != frame_counts[key])
			{
				frame_counts[key] = frameCount;
				break;
			}
			auto now = std::chrono::system_clock::now();
			std::chrono::duration<double> diff = now - start;
			if (diff.count() * 1000 > timeoutMillis)
			{
				// Sometimes sleep_for takes longer than expected, and also GetFrameCount()
				// takes a little time. Use the system clock to properly respect the timeout.
				break;
			}
			std::this_thread::sleep_for(std::chrono::microseconds(sleep_microseconds));
		}
	}

	// The "key" can be any integer. It will be used to keep a separate account of what counts as a "fresh" frame.
	// For example, frame number 67 may be fresh from bot1's perspective, but bot2 may have already seen it.
	extern "C" DLL_EXPORT ByteBuffer RLBOT_CORE_API FreshLiveDataPacketFlatbuffer(int timeoutMillis, int key)
	{
		waitForFrame(timeoutMillis, key);
		return UpdateLiveDataPacketFlatbuffer();
	}

	// The "key" can be any integer. It will be used to keep a separate account of what counts as a "fresh" frame.
	// For example, frame number 67 may be fresh from bot1's perspective, but bot2 may have already seen it.
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API FreshLiveDataPacket(LiveDataPacket* pLiveData, int timeoutMillis, int key)
	{
		waitForFrame(timeoutMillis, key);
		return UpdateLiveDataPacket(pLiveData);
	}

	bool hasFieldData() {
		return field_info_packet_flatbuffer_tcp.hasData();
	}
}
