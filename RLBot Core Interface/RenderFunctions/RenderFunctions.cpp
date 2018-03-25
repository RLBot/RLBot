#include "RenderFunctions.hpp"

//ToDo: Optimize code
#define BEGIN_RENDER_FUNCTION(structName, name)	CHECK_BUFFER_OVERFILLED(FileMappings::GetRenderInput(), false); \
												BEGIN_FUNCTION(structName, name, FileMappings::GetRenderInput())

#define END_RENDER_FUNCTION						END_FUNCTION(FileMappings::GetRenderInput())

namespace RenderFunctions
{
	static bool bRendering = false;

	extern "C" RLBotCoreStatus RLBOT_CORE_API BeginRendering()
	{
		RenderInput* pRenderInput = FileMappings::GetRenderInput();
		pRenderInput->Lock();
		pRenderInput->Reset();
		bRendering = true;

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API EndRendering()
	{
		RenderInput* pRenderInput = FileMappings::GetRenderInput();
		pRenderInput->Unlock();
		bRendering = false;

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API DrawLine2D(int x1, int y1, int x2, int y2, const Color& color)
	{
		BEGIN_RENDER_FUNCTION(DrawLine2DMessage, pLine2D);
		pLine2D->X1 = x1;
		pLine2D->Y1 = y1;
		pLine2D->X2 = x2;
		pLine2D->Y2 = y2;
		pLine2D->Color = color;
		END_RENDER_FUNCTION;

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API DrawLine3D(const Vector3& vec1, const Vector3& vec2, const Color& color)
	{
		BEGIN_RENDER_FUNCTION(DrawLine3DMessage, pLine3D);
		pLine3D->Vec1 = vec1;
		pLine3D->Vec2 = vec2;
		pLine3D->Color = color;
		END_RENDER_FUNCTION;

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API DrawLine2D_3D(int x, int y, const Vector3& vec, const Color& color)
	{
		BEGIN_RENDER_FUNCTION(DrawLine2D_3DMessage, pLine2D_3D);
		pLine2D_3D->X = x;
		pLine2D_3D->Y = y;
		pLine2D_3D->Vec = vec;
		pLine2D_3D->Color = color;
		END_RENDER_FUNCTION;

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API DrawRect2D(int x, int y, int width, int height, bool filled, const Color& color)
	{
		BEGIN_RENDER_FUNCTION(DrawRect2DMessage, pRect2D);
		pRect2D->X = x;
		pRect2D->Y = y;
		pRect2D->Width = width;
		pRect2D->Height = height;
		pRect2D->Filled = filled;
		pRect2D->Color = color;
		END_RENDER_FUNCTION;

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API DrawRect3D(const Vector3& vec, int width, int height, bool filled, const Color& color)
	{
		BEGIN_RENDER_FUNCTION(DrawRect3DMessage, pRect3D);
		pRect3D->Vec = vec;
		pRect3D->Width = width;
		pRect3D->Height = height;
		pRect3D->Filled = filled;
		pRect3D->Color = color;
		END_RENDER_FUNCTION;

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API DrawString2D(int x, int y, float scaleX, float scaleY, const Color& color, wchar_t* pString)
	{
		BEGIN_RENDER_FUNCTION(DrawString2DMessage, pString2D);
		pString2D->X = x;
		pString2D->Y = y;
		pString2D->ScaleX = scaleX;
		pString2D->ScaleY = scaleY;
		pString2D->Color = color;
		wcscpy(pString2D->String, pString);
		END_RENDER_FUNCTION;

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API DrawString3D(const Vector3& vec, float scaleX, float scaleY, const Color& color, wchar_t* pString)
	{
		BEGIN_RENDER_FUNCTION(DrawString3DMessage, pString3D);
		pString3D->Vec = vec;
		pString3D->ScaleX = scaleX;
		pString3D->ScaleY = scaleY;
		pString3D->Color = color;
		wcscpy(pString3D->String, pString);
		END_RENDER_FUNCTION;

		return RLBotCoreStatus::Success;
	}
}