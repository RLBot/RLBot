#ifndef MESSAGEPROCESSOR_HPP
#define MESSAGEPROCESSOR_HPP

#include <unordered_map>

#include "..\ErrorCodes\ErrorCodes.hpp"
#include "..\MessageDefines\MessageDefines.hpp"
#include "..\MessageStructs\CallbackMessages.hpp"
#include "..\MessageStructs\Message.hpp"

typedef RLBotCoreStatus (*MessageHandler)(MessageBase* pMessage);

#endif