#ifndef RENDERFUNCTIONS_HPP
#define RENDERFUNCTIONS_HPP

#include <Messages.hpp>

#include "..\BoostUtilities\BoostUtilities.hpp"
#include "..\InterfaceBase\InterfaceBase.hpp"

#ifdef __cplusplus
extern "C"
{
#endif

	namespace RenderFunctions
	{
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API BeginRendering();
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API EndRendering();
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API DrawLine2D(int x1, int y1, int x2, int y2, const PyStruct::Color& color);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API DrawLine3D(const PyStruct::Vector3& vec1, const PyStruct::Vector3& vec2, const PyStruct::Color& color);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API DrawLine2D_3D(int x, int y, const PyStruct::Vector3& vec, const PyStruct::Color& color);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API DrawRect2D(int x, int y, int width, int height, bool filled, const PyStruct::Color& color);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API DrawRect3D(const PyStruct::Vector3& vec, int width, int height, bool filled, const PyStruct::Color& color);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API DrawString2D(int x, int y, float scaleX, float scaleY, const PyStruct::Color& color, wchar_t* pString);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API DrawString3D(const PyStruct::Vector3& vec, float scaleX, float scaleY, const PyStruct::Color& color, wchar_t* pString);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API ToggleNullRenderer(bool Enable);

		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API RenderGroup(void* renderGroup, int protoSize);
	}

#ifdef __cplusplus
}
#endif

#endif