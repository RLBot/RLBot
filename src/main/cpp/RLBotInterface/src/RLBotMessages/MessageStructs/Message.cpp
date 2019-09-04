#include "Message.hpp"

#include "CallbackMessages.hpp"
#include "GameMessages.hpp"

static size_t ConstantSize(size_t size, MessageBase* pMessage) { return pMessage, size; }

std::function<size_t(MessageBase*)> MessageBase::GetSizeFunctions[MaxMessageType] = {
	std::bind(ConstantSize, sizeof(CallbackMessage), std::placeholders::_1),
	std::bind(ConstantSize, sizeof(StartMatchMessage), std::placeholders::_1),
	std::bind(ConstantSize, sizeof(SendChatMessage), std::placeholders::_1),
};