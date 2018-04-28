#ifndef INTERFACE_HPP
#define INTERFACE_HPP

#include <DebugHelper.hpp>

#include "GameFunctions\GameFunctions.hpp"
#include "RenderFunctions\RenderFunctions.hpp"

#ifdef __cplusplus
extern "C"
{
#endif

	namespace Interface
	{
		DLL_EXPORT bool RLBOT_CORE_API IsInitialized();
	}

#ifdef __cplusplus
}
#endif

#endif