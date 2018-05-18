#ifndef RENDERFUNCTIONS_HPP
#define RENDERFUNCTIONS_HPP

#include <Messages.hpp>

#include "..\InterfaceBase\InterfaceBase.hpp"

#ifdef __cplusplus
extern "C"
{
#endif

	namespace RenderFunctions
	{
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API RenderGroup(void* renderGroup, int protoSize);
	}

#ifdef __cplusplus
}
#endif

#endif