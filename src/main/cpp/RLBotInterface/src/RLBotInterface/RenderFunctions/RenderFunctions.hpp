#ifndef RENDERFUNCTIONS_HPP
#define RENDERFUNCTIONS_HPP

#include <Messages.hpp>
#include "Renderer.hpp"
#include "InterfaceBase/InterfaceBase.hpp"

#ifdef __cplusplus
extern "C"
{
#endif

	namespace RenderFunctions
	{
		void Initialize();

		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API RenderGroup(void* renderGroup, int protoSize);

		/*
			Exported functions of a rendering class. This can be used to generate the flatbuffers packets in c++ for excelent performance.
			Use with caution, wrong usage of these functions can cause memory leaks or very hard to debug crashes.

			Use the RenderGroup function instead.

			Only use this if your language of choice is very slow at generating flatbuffers packets. (Python)
		*/

		DLL_EXPORT Renderer* RLBOT_CORE_API Renderer_Constructor(int groupid);
		DLL_EXPORT void RLBOT_CORE_API Renderer_Destructor(Renderer* ptr);

		DLL_EXPORT void RLBOT_CORE_API Renderer_DrawLine3D(Renderer* ptr, Color color, PyStruct::Vector3 start, PyStruct::Vector3 end);
		DLL_EXPORT void RLBOT_CORE_API Renderer_DrawPolyLine3D(Renderer* ptr, Color color, PyStruct::Vector3* points, int count);
		DLL_EXPORT void RLBOT_CORE_API Renderer_DrawString2D(Renderer* ptr, const char* text, Color color, PyStruct::Vector3 upperLeft, int scaleX, int scaleY);
		DLL_EXPORT void RLBOT_CORE_API Renderer_DrawString3D(Renderer* ptr, const char* text, Color color, PyStruct::Vector3 upperLeft, int scaleX, int scaleY);
		DLL_EXPORT void RLBOT_CORE_API Renderer_DrawRect2D(Renderer* ptr, Color color, PyStruct::Vector3 upperLeft, int width, int height, bool filled);
		DLL_EXPORT void RLBOT_CORE_API Renderer_DrawRect3D(Renderer* ptr, Color color, PyStruct::Vector3 upperLeft, int width, int height, bool filled, bool centered);
		DLL_EXPORT void RLBOT_CORE_API Renderer_Clear(Renderer* ptr);
		DLL_EXPORT void RLBOT_CORE_API Renderer_FinishAndSend(Renderer* ptr);
	}

#ifdef __cplusplus
}
#endif

#endif