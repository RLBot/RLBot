#include "RLBotSockets/bot_client.hpp"
#include "GameFunctions/GameFunctions.hpp"
#include "GameFunctions/PlayerInfo.hpp"
#include "GameFunctions/BallPrediction.hpp"

#include <cmath>
#include <iostream>
#include <DebugHelper.hpp>

inline boost::asio::ip::address localhost = boost::asio::ip::address::from_string("127.0.0.1");

namespace BotClientStatic {

	static BotClient* bot_client;

	BotClient* botClientInstance() {
		return bot_client;
	}

	void initBotClient(int port, boost::asio::io_context* ioc) {
		bot_client = new BotClient(*ioc, port);
	}
}

BotClient::BotClient(boost::asio::io_context & ioc, int port) :
	endpoint(localhost, port),
	socket(ioc), 
	is_connected(false) {

	connect();
}

void BotClient::connect() {
  socket.async_connect(endpoint, [this](boost::system::error_code error){
	  if (error) {
		  DEBUG_LOG("DLL client failed to connect, retrying...\n");
		  connect();
	  }
	  else {
		  DEBUG_LOG("DLL client connected!\n");
		  is_connected = true;
		  socket.set_option(boost::asio::ip::tcp::no_delay(true));
		  socket.set_option(boost::asio::socket_base::send_buffer_size(524288));
		  socket.set_option(boost::asio::socket_base::receive_buffer_size(524288));
		  respond_loop();
	  }
  });
}

void BotClient::write(std::string str, TcpClient::DataType data_type) {

	boost::system::error_code error;

	char short_buf[2];

	const std::lock_guard<std::mutex> lock(write_mutex);

	TcpClient::serializeShort(short_buf, data_type);
	boost::asio::write(socket, boost::asio::buffer(short_buf, 2), error);
	if (error) {
		printf("Error writing datatype header: %s\n", error.message().c_str());
		return;
	}

	uint16_t size = uint16_t(str.size());
	TcpClient::serializeShort(short_buf, size);
	boost::asio::write(socket, boost::asio::buffer(short_buf, 2), error);
	if (error) {
		printf("Error writing size header: %s\n", error.message().c_str());
		return;
	}

	boost::asio::write(socket, boost::asio::buffer(str), error);
	if (error) {
		printf("Error writing payload: %s\n", error.message().c_str());
		return;
	}

}

void BotClient::respond_loop() {

	boost::asio::async_read(socket, read_buffer, boost::asio::transfer_exactly(2),
		[&, this](boost::system::error_code read_error, std::size_t bytes_transferred) {

		message_type = (TcpClient::DataType) TcpClient::readShort(read_buffer);

		boost::system::error_code size_error;
		boost::asio::streambuf size_buffer(2);
		boost::asio::read(socket, size_buffer, boost::asio::transfer_exactly(2), size_error);
		if (size_error) {
			printf("error reading message size: %s\n", size_error.message().c_str());
			return;
		}

		message_size = (TcpClient::DataType) TcpClient::readShort(size_buffer);

		// printf("Got message type %i with size %i\n", message_type, message_size);

		boost::system::error_code payload_error;
		boost::asio::read(socket, boost::asio::buffer(message.data(), message_size), boost::asio::transfer_exactly(message_size), payload_error);
		if(payload_error) {
			printf("error reading payload: %s\n", payload_error.message().c_str());
			return;
		}

		switch (message_type) {
		case TcpClient::DataType::live_data_packet:
			GameFunctions::setGameTickPacketFlatbuffer(std::string(message.data(), message_size));
			break;
		case TcpClient::DataType::field_info_packet:
			GameFunctions::setFieldInfoPacketFlatbuffer(std::string(message.data(), message_size));
			break;
		case TcpClient::DataType::rlbot_match_settings:
			GameFunctions::setMatchSettingsFlatbuffer(std::string(message.data(), message_size));
			break;
		case TcpClient::DataType::rlbot_quick_chat:
			GameFunctions::appendReceivedChatMessage(std::string(message.data(), message_size));
			break;
		case TcpClient::DataType::ball_prediction:
			BallPrediction::setBallPredictionFlatbuffer(std::string(message.data(), message_size));
		}

		respond_loop();
    }
  );

};