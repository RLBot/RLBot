#include "RenderFunctions.hpp"
#include <BoostUtilities\BoostConstants.hpp>
#include <BoostUtilities\BoostUtilities.hpp>

namespace RenderFunctions
{
	BoostUtilities::QueueSender* pRenderGroupQueue = nullptr;

	void Initialize()
	{
		pRenderGroupQueue = new BoostUtilities::QueueSender(BoostConstants::RenderingFlatQueueName);
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API RenderGroup(void* renderGroup, int protoSize)
	{
		return pRenderGroupQueue->sendMessage(renderGroup, protoSize);
	}
}
