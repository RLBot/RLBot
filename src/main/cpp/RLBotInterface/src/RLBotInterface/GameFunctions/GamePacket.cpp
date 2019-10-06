#include <thread>
#include <DebugHelper.hpp>

#include "GamePacket.hpp"
#include <MessageTranslation/FlatbufferTranslator.hpp>
#include <BoostUtilities/BoostUtilities.hpp>
#include <BoostUtilities/BoostConstants.hpp>

namespace GameFunctions
{
	BoostUtilities::SharedMemReader* pFlatFieldMem = nullptr;
	BoostUtilities::SharedMemReader* pFlatTickMem = nullptr;
	BoostUtilities::SharedMemReader* pPhysicsTickMem = nullptr;
	BoostUtilities::SharedMemReader* pMatchSettingsReader = nullptr;
	BoostUtilities::SharedByteReader* pFrameCountReader = nullptr;

	static std::map<int, char> frame_counts;

	ByteBuffer MakeEmptyBuffer()
	{
		ByteBuffer empty;
		empty.ptr = new char[1]; // Arbitrary valid pointer to an array. We'll be calling delete[] on this later.
		empty.size = 0;
		return empty;
	}

	void Initialize_GamePacket()
	{
		pFlatFieldMem = new BoostUtilities::SharedMemReader(BoostConstants::FieldInfoFlatName);
		pFlatTickMem = new BoostUtilities::SharedMemReader(BoostConstants::GameDataFlatName);
		pPhysicsTickMem = new BoostUtilities::SharedMemReader(BoostConstants::PhysicsTickFlatName);
		pMatchSettingsReader = new BoostUtilities::SharedMemReader(BoostConstants::MatchSettingsName);
		pFrameCountReader = new BoostUtilities::SharedByteReader(BoostConstants::FrameCountName);
	}

	void Uninitialize_GamePacket()
	{
		pFlatFieldMem->unlockMutex();
		pFlatTickMem->unlockMutex();
		pPhysicsTickMem->unlockMutex();
	}

	//////////////
	// FIELD INFO
	//////////////

	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoFlatbuffer()
	{
		if (!pFlatFieldMem)
		{
			return MakeEmptyBuffer();
		}
		return pFlatFieldMem->fetchData();
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

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketFlatbuffer()
	{
		if (!pFlatTickMem)
		{
			return MakeEmptyBuffer();
		}
		return pFlatTickMem->fetchData();
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
		if (!pPhysicsTickMem)
		{
			return MakeEmptyBuffer();
		}
		return pPhysicsTickMem->fetchData();
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateRigidBodyTick(RigidBodyTick* rigidBodyTick)
	{
		ByteBuffer flatbuffer = UpdateRigidBodyTickFlatbuffer();
		FlatbufferTranslator::translateToRigidBodyStruct(flatbuffer, rigidBodyTick);
		delete[] flatbuffer.ptr;

		return RLBotCoreStatus::Success;
	}

	extern "C" DLL_EXPORT ByteBuffer RLBOT_CORE_API GetMatchSettings()
	{
		if (!pMatchSettingsReader)
		{
			return MakeEmptyBuffer();
		}
		return pMatchSettingsReader->fetchData();
	}

	///////////////
	// FRESH PACKETS
	///////////////

	char GetFrameCount()
	{
		if (!pFrameCountReader)
		{
			return 0;
		}
		return pFrameCountReader->fetchByte();
	}

	static const int sleep_microseconds = 500;

	void waitForFrame(int timeoutMillis, int key)
	{
		auto start = std::chrono::system_clock::now();

		// The for loop is not strictly necessary because we'll generally break sooner due to
		// the system clock registering the timeout. Still using the for loop rather than a
		// while(true) out of an abundance of caution.
		for (int i = 0; i < timeoutMillis * 1000 / sleep_microseconds; i++) {
			int frameCount = GetFrameCount();
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
}