#include "BoostUtilities.hpp"
#include "BoostConstants.hpp"

#include "stdlib.h"

namespace BoostUtilities
{
	QueueSender::QueueSender(const char* queueName)
	{
		pQueue = new interop_message_queue(boost::interprocess::open_only, queueName);
	}

	SharedMemReader::SharedMemReader(const char* name)
	{
		// The intermediate variables in this function are necessary for some reason.
		std::string sharedMemName = BoostConstants::buildSharedMemName(name);
		const char* sharedMemChar = sharedMemName.c_str();
		pSharedMem = new boost::interprocess::shared_memory_object(boost::interprocess::open_only, sharedMemChar, boost::interprocess::read_only);
		
		std::string mutexName = BoostConstants::buildMutexName(name);
		const char* mutexChar = mutexName.c_str();
		pMutex = new boost::interprocess::named_sharable_mutex(boost::interprocess::open_only, mutexChar);
	}

	ByteBuffer SharedMemReader::fetchData() 
	{
		// The lock will be released when this object goes out of scope
		boost::interprocess::sharable_lock<boost::interprocess::named_sharable_mutex> myLock(*pMutex);
		hasLock = true;

		boost::interprocess::offset_t size;
		pSharedMem->get_size(size);

		if (size == 0)
		{
			// Bail out early because mapped_region will freak out if size is zero.
			ByteBuffer empty;
			empty.ptr = new char[1]; // Arbitrary valid pointer to an array. We'll be calling delete[] on this later.
			empty.size = 0;
			return empty;
		}

		boost::interprocess::mapped_region region(*pSharedMem, boost::interprocess::read_only);
		unsigned char *buffer = new unsigned char[region.get_size()];
		memcpy(buffer, region.get_address(), region.get_size());

		ByteBuffer buf;
		buf.ptr = buffer;
		buf.size = region.get_size();

		hasLock = false;

		return buf;
	}

	void SharedMemReader::unlockMutex()
	{
		if (hasLock)
		{
			pMutex->unlock_sharable();
			hasLock = false;
		}
	}

	SharedMemWriter::SharedMemWriter(const char* name)
	{
		// The intermediate variables in this function are necessary for some reason.

		pMemName = name;

		std::string sharedMemName = BoostConstants::buildSharedMemName(name);
		const char* sharedMemChar = sharedMemName.c_str();
		boost::interprocess::shared_memory_object::remove(sharedMemChar);
		pSharedMem = new boost::interprocess::shared_memory_object(boost::interprocess::create_only, sharedMemChar, boost::interprocess::read_write);

		std::string mutexName = BoostConstants::buildMutexName(name);
		const char* mutexChar = mutexName.c_str();
		boost::interprocess::named_sharable_mutex::remove(mutexChar);
		pMutex = new boost::interprocess::named_sharable_mutex(boost::interprocess::create_only, mutexChar);
	}

	SharedMemWriter::~SharedMemWriter()
	{
		std::string mutexName = BoostConstants::buildMutexName(pMemName);
		const char* mutexChar = mutexName.c_str();
		boost::interprocess::named_sharable_mutex::remove(mutexChar);
		boost::interprocess::shared_memory_object::remove(pSharedMem->get_name());
	}

	void SharedMemWriter::writeData(void* address, int size)
	{
		// The lock will be released when this object goes out of scope, i.e. when this function exits.
		boost::interprocess::scoped_lock<boost::interprocess::named_sharable_mutex> myLock(*pMutex);

		pSharedMem->truncate(size);
		if (size > 0)
		{
			boost::interprocess::mapped_region region(*pSharedMem, boost::interprocess::read_write);
			std::memcpy(region.get_address(), address, size);
		}
	}

	RLBotCoreStatus QueueSender::sendMessage(void* message, int messageSize)
	{
		if (messageSize > pQueue->get_max_msg_size())
		{
			return RLBotCoreStatus::MessageLargerThanMax;
		}

		bool sent = pQueue->try_send(message, messageSize, 0);

		if (!sent)
		{
			return RLBotCoreStatus::BufferOverfilled;
		}
		return RLBotCoreStatus::Success;
	}

	SharedByteReader::SharedByteReader(const char* name)
	{
		// The intermediate variables in this function are necessary for some reason.
		std::string sharedMemName = BoostConstants::buildSharedMemName(name);
		const char* sharedMemChar = sharedMemName.c_str();
		pSharedMem = new boost::interprocess::shared_memory_object(boost::interprocess::open_only, sharedMemChar, boost::interprocess::read_only);
	}

	char SharedByteReader::fetchByte()
	{
		boost::interprocess::offset_t size;
		pSharedMem->get_size(size);

		if (size == 0)
		{
			// Bail out early because mapped_region will freak out if size is zero.
			return 0;
		}

		boost::interprocess::mapped_region region(*pSharedMem, boost::interprocess::read_only);
		unsigned char *buffer = new unsigned char[1];
		memcpy(buffer, region.get_address(), 1);
		return buffer[0];
	}

	SharedByteWriter::SharedByteWriter(const char* name)
	{
		// The intermediate variables in this function are necessary for some reason.

		pMemName = name;

		std::string sharedMemName = BoostConstants::buildSharedMemName(name);
		const char* sharedMemChar = sharedMemName.c_str();
		boost::interprocess::shared_memory_object::remove(sharedMemChar);
		pSharedMem = new boost::interprocess::shared_memory_object(boost::interprocess::create_only, sharedMemChar, boost::interprocess::read_write);
		pSharedMem->truncate(1);
	}

	SharedByteWriter::~SharedByteWriter()
	{
		boost::interprocess::shared_memory_object::remove(pSharedMem->get_name());
	}

	void SharedByteWriter::writeByte(char data)
	{
		char dataArr[] = { data };
		boost::interprocess::mapped_region region(*pSharedMem, boost::interprocess::read_write);
		std::memcpy(region.get_address(), dataArr, 1);
	}

}
