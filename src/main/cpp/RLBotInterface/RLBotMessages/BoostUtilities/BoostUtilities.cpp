#include "BoostUtilities.hpp"

namespace GameFunctions {

	ByteBuffer fetchByteBufferFromSharedMem(boost::interprocess::shared_memory_object* shm, boost::interprocess::named_sharable_mutex* mtx)
	{
		// The lock will be released when this object goes out of scope
		boost::interprocess::sharable_lock<boost::interprocess::named_sharable_mutex> myLock(*mtx);

		boost::interprocess::offset_t size;
		shm->get_size(size);
		if (size == 0)
		{
			// Bail out early because mapped_region will freak out if size is zero.
			ByteBuffer empty;
			empty.ptr = new char[1]; // Arbitrary valid pointer to an array. We'll be calling delete[] on this later.
			empty.size = 0;
			return empty;
		}

		boost::interprocess::mapped_region region(*shm, boost::interprocess::read_only);
		unsigned char *buffer = new unsigned char[region.get_size()];
		memcpy(buffer, region.get_address(), region.get_size());

		ByteBuffer buf;
		buf.ptr = buffer;
		buf.size = region.get_size();

		return buf;
	}

}
