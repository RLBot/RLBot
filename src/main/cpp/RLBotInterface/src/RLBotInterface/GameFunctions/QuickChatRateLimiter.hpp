#pragma once
#include <PacketStructs/LiveDataPacket.hpp>
#include <ErrorCodes/ErrorCodes.hpp>
#include <time.h>
#include <map>

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
		std::map<int, ChatState> chatStates;
	public:
		QuickChatRateLimiter()
		{ }
		
		RLBotCoreStatus CanSendChat(int playerIndex);
		void RecordQuickChatSubmission(int playerIndex);
	};

}

