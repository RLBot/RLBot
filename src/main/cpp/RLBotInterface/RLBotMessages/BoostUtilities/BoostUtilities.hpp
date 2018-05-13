#ifndef BOOSTUTILITIES_HPP
#define BOOSTUTILITIES_HPP

#include "../Messages.hpp"

#include <boost\interprocess\ipc\message_queue.hpp>
#include <boost/interprocess/shared_memory_object.hpp>
#include <boost/interprocess/mapped_region.hpp>
#include <boost\interprocess\sync\named_sharable_mutex.hpp>
#include <boost\interprocess\sync\sharable_lock.hpp>

#include "BoostConstants.hpp"

// Adds the proto to the boost queue with message size checking and buffer size checking
#define ADD_TO_BOOST_QUEUE(queue, proto, protosize, maxsize)	if (protosize >= maxsize) { \
																	return RLBotCoreStatus::MessageLargerThanMax; \
																} \
																bool sent = queue.try_send(proto, protosize, 0); \
																if (!sent) { \
																	return RLBotCoreStatus::BufferOverfilled; \
																} \
																return RLBotCoreStatus::Success; \


// Currently we are relying on the core dll to create the queue in shared memory before this process starts. TODO: be less fragile
#define CREATE_CLIENT_BOOST_QUEUE(variable_name, queue)	static interop_message_queue variable_name(boost::interprocess::open_only, queue);


#define CREATE_CLIENT_BOOST_SHARED_MEMORY(memVariable, memConstant, mutexVariable, mutextConstant) \
	static boost::interprocess::shared_memory_object memVariable( \
		boost::interprocess::open_only, memConstant, boost::interprocess::read_only); \
	\
	static boost::interprocess::named_sharable_mutex mutexVariable( \
		boost::interprocess::open_only, mutextConstant);

/*
This typedef is advice from one of the boost maintainers on how to make message queues work between 32 and 64 bit processes.
It looks pretty janky. I believe the reason it's not "fixed" in the library is that it can't be done consistently on windows vs linux.

"In general I regret putting message_queue in Interprocess, as IMHO it's not good enough to be in the library. Some people find it useful, though."
https://lists.boost.org/Archives/boost/2014/06/214746.php
*/
typedef boost::interprocess::message_queue_t< boost::interprocess::offset_ptr<void, boost::int32_t, boost::uint64_t>> interop_message_queue;

namespace GameFunctions {

	// Gets the next ByteBuffer from a boost shared memory with the given object and mutex
	ByteBuffer fetchByteBufferFromSharedMem(boost::interprocess::shared_memory_object* shm, boost::interprocess::named_sharable_mutex* mtx);
}

#endif