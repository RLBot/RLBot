#pragma once

#include <string>
#include <mutex>
#include <shared_mutex>
#include "MessageStructs/ByteBuffer.hpp"

class SafeFlatbufferHolder
{
public:
	SafeFlatbufferHolder()
		: data("")
		, m()
	{}

	~SafeFlatbufferHolder()
	{}

	// Add an element to the queue.
	void set(std::string s)
	{
		std::unique_lock lock(m);
		data = s;
	}

	bool hasData()
	{
		return data.size() > 0;
	}

	ByteBuffer copyOut()
	{
		std::shared_lock lock(m);

		int size = data.size();
		if (size == 0) {
			return makeEmptyBuffer();
		}
		unsigned char *buffer = new unsigned char[size];
		memcpy(buffer, data.data(), size);

		ByteBuffer buf;
		buf.ptr = buffer;
		buf.size = size;

		return buf;
	}

private:
	std::string data;
	mutable std::shared_mutex m;

	ByteBuffer makeEmptyBuffer()
	{
		ByteBuffer empty;
		empty.ptr = new char[1]; // Arbitrary valid pointer to an array. We'll be calling delete[] on this later.
		empty.size = 0;
		return empty;
	}
};
