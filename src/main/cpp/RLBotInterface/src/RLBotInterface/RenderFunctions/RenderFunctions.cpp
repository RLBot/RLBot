#include "RenderFunctions.hpp"
#include "RLBotSockets/bot_client.hpp"

namespace RenderFunctions
{

	extern "C" RLBotCoreStatus RLBOT_CORE_API RenderGroup(void* renderGroup, int size)
	{
		std::string render_message((char *)renderGroup, size);
		BotClientStatic::botClientInstance()->write(render_message, TcpClient::DataType::rlbot_render_group);
		return RLBotCoreStatus::Success;
	}

	extern "C" Renderer* Renderer_Constructor(int groupid)
	{
		return new Renderer(groupid);
	}

	extern "C" void Renderer_Destructor(Renderer* ptr)
	{
		delete ptr;
	}

	extern "C" void Renderer_DrawLine3D(Renderer* ptr, Color color, PyStruct::Vector3 start, PyStruct::Vector3 end)
	{
		ptr->DrawLine3D(color, start, end);
	}

	extern "C" void Renderer_DrawPolyLine3D(Renderer* ptr, Color color, PyStruct::Vector3* points, int count)
	{
		ptr->DrawPolyLine3D(color, points, count);
	}

	extern "C" void Renderer_DrawString2D(Renderer* ptr, const char* text, Color color, PyStruct::Vector3 upperLeft, int scaleX, int scaleY)
	{
		ptr->DrawString2D(std::string(text), color, upperLeft, scaleX, scaleY);
	}

	extern "C" void Renderer_DrawString3D(Renderer* ptr, const char* text, Color color, PyStruct::Vector3 upperLeft, int scaleX, int scaleY) 
	{
		ptr->DrawString3D(std::string(text), color, upperLeft, scaleX, scaleY);
	}

	extern "C" void Renderer_DrawRect2D(Renderer* ptr, Color color, PyStruct::Vector3 upperLeft, int width, int height, bool filled)
	{
		ptr->DrawRect2D(color, upperLeft, width, height, filled);
	}

	extern "C" void Renderer_DrawRect3D(Renderer* ptr, Color color, PyStruct::Vector3 upperLeft, int width, int height, bool filled, bool centered)
	{
		ptr->DrawRect3D(color, upperLeft, width, height, filled, centered);
	}
	
	extern "C" void Renderer_Clear(Renderer* ptr)
	{
		ptr->Clear();
	}

	extern "C" void Renderer_FinishAndSend(Renderer* ptr)
	{
		ptr->FinishAndSend();
	}
}
