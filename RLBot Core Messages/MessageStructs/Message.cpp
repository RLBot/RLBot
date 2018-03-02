#include "Message.hpp"

#include "CallbackMessages.hpp"
#include "GameMessages.hpp"
#include "RendererMessages.hpp"

static size_t ConstantSize(size_t size, MessageBase* pMessage) { return pMessage, size; }

std::function<size_t(MessageBase*)> GetSizeFunctions[MaxMessageType] = {
	std::bind(ConstantSize, sizeof(CallbackMessage), std::placeholders::_1),
	std::bind(ConstantSize, sizeof(StartMatchMessage), std::placeholders::_1),
	std::bind(ConstantSize, sizeof(UpdatePlayerInputMessage), std::placeholders::_1),
	std::bind(ConstantSize, sizeof(SendChatMessage), std::placeholders::_1),
	std::bind(ConstantSize, sizeof(DrawLine2DMessage), std::placeholders::_1),
	std::bind(ConstantSize, sizeof(DrawLine3DMessage), std::placeholders::_1),
	std::bind(ConstantSize, sizeof(DrawLine2D_3DMessage), std::placeholders::_1),
	std::bind(ConstantSize, sizeof(DrawRect2DMessage), std::placeholders::_1),
	std::bind(ConstantSize, sizeof(DrawRect3DMessage), std::placeholders::_1),
	[](MessageBase* msg) -> size_t { return sizeof(DrawString2DMessage) + wcslen(((DrawString2DMessage*)msg)->String) * 2; },
	[](MessageBase* msg) -> size_t { return sizeof(DrawString3DMessage) + wcslen(((DrawString3DMessage*)msg)->String) * 2; }
};