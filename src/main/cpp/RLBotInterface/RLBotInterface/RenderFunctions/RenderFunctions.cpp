#include "RenderFunctions.hpp"
#include <BoostUtilities\BoostConstants.hpp>
#include <BoostUtilities\BoostUtilities.hpp>

namespace RenderFunctions
{
	static BoostUtilities::QueueSender renderGroupQueue(BoostConstants::RenderingFlatQueueName);

	extern "C" RLBotCoreStatus RLBOT_CORE_API RenderGroup(void* renderGroup, int protoSize)
	{
		return renderGroupQueue.sendMessage(renderGroup, protoSize);
	}
}
