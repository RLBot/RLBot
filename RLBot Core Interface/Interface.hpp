#ifndef INTERFACE_HPP
#define INTERFACE_HPP

#include <SDK.hpp>

#include "GameFunctions\GameFunctions.hpp"
#include "RenderFunctions\RenderFunctions.hpp"

#define END_GAME_FUNCTION						END_FUNCTION(pGameInput, pGameMessage); \
												FileMappings::Unlock(pGameInput)

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