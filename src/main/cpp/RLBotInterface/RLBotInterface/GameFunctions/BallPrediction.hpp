#ifndef GAMEPACKET_HPP
#define GAMEPACKET_HPP

#include <MessageStructs\ByteBuffer.hpp>
#include "..\InterfaceBase\InterfaceBase.hpp"


#ifdef __cplusplus
extern "C"
{
#endif

	namespace BallPrediction
	{
		DLL_EXPORT ByteBuffer RLBOT_CORE_API GetBallPrediction();
	}

#ifdef __cplusplus
}
#endif

#endif