#pragma once
#include <PacketStructs\LiveDataPacket.hpp>
#include <ErrorCodes\ErrorCodes.hpp>
#include <time.h>

#define CONST_ChatReplenishMilliseconds 2000
#define CONST_MaxChatCount 5

namespace QuickChat {

	struct ChatState
	{
		long long windowStartTime;
		int chatCounter;
	};

	class QuickChatRateLimiter
	{

	private:
		ChatState chatStates[CONST_MaxPlayers];
	public:
		QuickChatRateLimiter() : chatStates{0}
		{ }
		
		RLBotCoreStatus CanSendChat(int playerIndex);
		void RecordQuickChatSubmission(int playerIndex);
	};

}

