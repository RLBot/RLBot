#pragma once

#define _WIN32_WINNT 0x0601
#include <boost/asio.hpp>

#include <array>
#include <string>
#include "TCP\TcpClient.hpp"
#include <mutex>



struct BotClient {

  BotClient(boost::asio::io_context & io, int port);

  void connect();

  void write(std::string str, TcpClient::DataType data_type);

  void respond_loop();

  boost::asio::ip::tcp::socket socket;
  boost::asio::ip::tcp::endpoint endpoint;
  boost::asio::streambuf read_buffer;

  std::mutex write_mutex;

  uint16_t message_size;
  TcpClient::DataType message_type;
  bool is_connected;

  std::array < char, 65536 > message;

};

namespace BotClientStatic {
	BotClient* botClientInstance();
	void initBotClient(int port, boost::asio::io_context* ioc);
}