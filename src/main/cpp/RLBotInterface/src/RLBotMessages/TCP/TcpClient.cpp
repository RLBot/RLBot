#include <stdio.h>
#include <chrono>
#include <thread>
#include <csignal>

#include <rlbot_generated.h>
#include <MessageTranslation/StructToRLBotFlatbuffer.hpp>

#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/detail/endian.hpp>

#include "TcpClient.hpp"


namespace TcpClient {

	using boost::asio::ip::tcp;

	// Messages are sent over the tcp socket, where the first 2 bytes represent the size of the message,
	// followed by the message payload (the flatbuffers binary data)
	unsigned short readShort(boost::asio::streambuf& streambuf)
	{
		std::istream istream(&streambuf);

		unsigned char first_byte = istream.get();
		unsigned char second_byte = istream.get();

		if (USE_LITTLE_ENDIAN)
		{
			return first_byte | second_byte << 8;
		}
		else
		{
			return second_byte | first_byte << 8;
		}
	}


	// Reads from the socket into the supplied data pointer.
	// After calling this function, the data should be ready for flatbuffer access.
	// A lot of this code is taken from https://stackoverflow.com/a/28931673
	// Returns the size of the data that was placed into the data param.
	int receiveSizePrefixedData(char* data, tcp::socket* socket)
	{
		boost::system::error_code error;

		boost::asio::streambuf read_buffer;

		// TODO: consider using asynchronous reads. This is susceptible to blocking forever and keeping a zombie RLBot.exe alive.
		std::size_t bytes_transferred = boost::asio::read(*socket, read_buffer, boost::asio::transfer_exactly(2), error);

		if (error == boost::asio::error::eof)
			return 0; // Connection closed cleanly by peer.
		else if (error)
			throw boost::system::system_error(error); // Some other error.

		int message_size = readShort(read_buffer);
		bytes_transferred = boost::asio::read(*socket, read_buffer, boost::asio::transfer_exactly(message_size), error);

		if (error == boost::asio::error::eof)
			return false; // Connection closed cleanly by peer.
		else if (error)
			throw boost::system::system_error(error); // Some other error.

		read_buffer.sgetn(data, message_size);

		return message_size;
	}

	int receiveTypeAndSizePrefixedData(char* data, DataType* data_type, tcp::socket* socket)
	{
		boost::system::error_code error;
		boost::asio::streambuf read_buffer;

		// TODO: consider using asynchronous reads. This is susceptible to blocking forever and keeping a zombie RLBot.exe alive.
		boost::asio::read(*socket, read_buffer, boost::asio::transfer_exactly(2), error);

		if (error == boost::asio::error::eof)
			return 0; // Connection closed cleanly by peer.
		else if (error)
			throw boost::system::system_error(error); // Some other error.

		*data_type = (DataType)TcpClient::readShort(read_buffer);

		return TcpClient::receiveSizePrefixedData(data, socket);
	}

	void serializeShort(char(&buf)[2], short val)
	{
		char most_significant_byte = (val >> 8) & 0xFF;
		char least_significant_byte = (val) & 0xFF;

		if (USE_LITTLE_ENDIAN)
		{
			buf[0] = least_significant_byte;
			buf[1] = most_significant_byte;
		}
		else
		{
			buf[0] = most_significant_byte;
			buf[1] = least_significant_byte;
		}
	}

}
