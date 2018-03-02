#ifndef CALLBACKMESSAGES_HPP
#define CALLBACKMESSAGES_HPP

#include <SDK.hpp>

#include "Message.hpp"

#include "..\ErrorCodes\ErrorCodes.hpp"
#include "..\PacketStructs\PacketStructs.hpp"

struct CallbackMessage : public Message<CallbackMessageType, false>
{
	unsigned int	FunctionID;
	RLBotCoreStatus	Status;
};

#endif