#include "QuickChatRateLimiter.hpp"
#include <chrono>
#include <rlbot_generated.h>
#include <BoostUtilities\BoostUtilities.hpp>

namespace QuickChat {

	long long GetCurrentTime()
	{
		using namespace std::chrono;

		// get the current time
		const auto now = system_clock::now();

		milliseconds duration = duration_cast<milliseconds>(now.time_since_epoch());

		return duration.count();
	}

	// Returns the Success status if quick chat is allowed.
	// InvalidPlayerIndex if the player index is out of bounds.
	// QuickChatRateExceeded if this player has been chatting too much during the current time window.
	RLBotCoreStatus QuickChatRateLimiter::CanSendChat(int playerIndex)
	{
		using namespace std::chrono;

		if (playerIndex < 0 || playerIndex >= CONST_MaxPlayers) 
		{
			return RLBotCoreStatus::InvalidPlayerIndex;
		}

		// Fetch the chat state associated with this player index.
		ChatState* chatState = &chatStates[playerIndex];

		long long now = GetCurrentTime();
		long long msSinceWindowStart = now - chatState->windowStartTime;
		if (msSinceWindowStart >= CONST_ChatReplenishMilliseconds)
		{
			chatState->windowStartTime = now;
			chatState->chatCounter = 0;
		}

		if (chatState->chatCounter < CONST_MaxChatCount) 
		{
			return RLBotCoreStatus::Success;
		}
		else
		{
			return RLBotCoreStatus::QuickChatRateExceeded;
		}		
	}

	// Records the fact that a quick chat is being sent for this player.
	void QuickChatRateLimiter::RecordQuickChatSubmission(int playerIndex)
	{
		chatStates[playerIndex].chatCounter++;
	}

}

