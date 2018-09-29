#include "BoostUtilities.hpp"
#include "BoostConstants.hpp"

namespace BoostUtilities {

	
	SharedMemReader::SharedMemReader(const char* name)
	{
		// The intermediate variables in this function are necessary for some reason.

		std::string sharedMemName = BoostConstants::buildSharedMemName(name);
		const char* sharedMemChar = sharedMemName.c_str();
		sharedMem = new boost::interprocess::shared_memory_object(boost::interprocess::open_only, sharedMemChar, boost::interprocess::read_only);

		std::string mutexName = BoostConstants::buildMutexName(name);
		const char* mutexChar = mutexName.c_str();
		mutex = new boost::interprocess::named_sharable_mutex(boost::interprocess::open_only, mutexChar);
	}

	ByteBuffer SharedMemReader::fetchData() 
	{
		// The lock will be released when this object goes out of scope
		boost::interprocess::sharable_lock<boost::interprocess::named_sharable_mutex> myLock(*mutex);

		boost::interprocess::offset_t size;
		sharedMem->get_size(size);
		if (size == 0)
		{
			// Bail out early because mapped_region will freak out if size is zero.
			ByteBuffer empty;
			empty.ptr = new char[1]; // Arbitrary valid pointer to an array. We'll be calling delete[] on this later.
			empty.size = 0;
			return empty;
		}

		boost::interprocess::mapped_region region(*sharedMem, boost::interprocess::read_only);
		unsigned char *buffer = new unsigned char[region.get_size()];
		memcpy(buffer, region.get_address(), region.get_size());

		ByteBuffer buf;
		buf.ptr = buffer;
		buf.size = region.get_size();

		return buf;
	}

	SharedMemWriter::SharedMemWriter(const char* name)
	{
		// The intermediate variables in this function are necessary for some reason.

		memName = name;

		std::string sharedMemName = BoostConstants::buildSharedMemName(name);
		const char* sharedMemChar = sharedMemName.c_str();
		boost::interprocess::shared_memory_object::remove(sharedMemChar);
		sharedMem = new boost::interprocess::shared_memory_object(boost::interprocess::create_only, sharedMemChar, boost::interprocess::read_write);

		std::string mutexName = BoostConstants::buildMutexName(name);
		const char* mutexChar = mutexName.c_str();
		boost::interprocess::named_sharable_mutex::remove(mutexChar);
		mutex = new boost::interprocess::named_sharable_mutex(boost::interprocess::create_only, mutexChar);
	}

	SharedMemWriter::~SharedMemWriter()
	{
		std::string mutexName = BoostConstants::buildMutexName(memName);
		const char* mutexChar = mutexName.c_str();
		boost::interprocess::named_sharable_mutex::remove(mutexChar);
		boost::interprocess::shared_memory_object::remove(sharedMem->get_name());
	}

	void SharedMemWriter::writeData(void* address, int size) {

		// The lock will be released when this object goes out of scope, i.e. when this function exits.
		boost::interprocess::scoped_lock<boost::interprocess::named_sharable_mutex> myLock(*mutex);

		sharedMem->truncate(size);
		if (size > 0)
		{
			boost::interprocess::mapped_region region(*sharedMem, boost::interprocess::read_write);
			std::memcpy(region.get_address(), address, size);
		}
	}

	RLBotCoreStatus QueueSender::sendMessage(void* message, int messageSize)
	{
		if (messageSize > queue.get_max_msg_size()) {
			return RLBotCoreStatus::MessageLargerThanMax;
		}

		bool sent = queue.try_send(message, messageSize, 0);
		if (!sent) {
			return RLBotCoreStatus::BufferOverfilled;
		}
		return RLBotCoreStatus::Success;
	}

}
