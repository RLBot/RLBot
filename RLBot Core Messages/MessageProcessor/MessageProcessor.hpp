#ifndef MESSAGEPROCESSOR_HPP
#define MESSAGEPROCESSOR_HPP

#include <unordered_map>

#include "..\ErrorCodes\ErrorCodes.hpp"
#include "..\MessageStructs\Message.hpp"

typedef RLBotCoreStatus (*MessageHandler)(MessageBase* pMessage);

class MessageProcessor
{
private:
	std::unordered_map<MessageType, MessageHandler> messageHandlerMap;

public:
	void SubscribeMessage(MessageType type, MessageHandler handler);
	void ProcessMessages(MessageBase* pFirst, size_t numMessages);
};

#endif