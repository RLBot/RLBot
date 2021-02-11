#pragma once

#include <boost/asio.hpp>
#include <flatbuffers/flatbuffers.h>

#define USE_LITTLE_ENDIAN 0

namespace TcpClient {

	enum DataType : uint16_t { 
		default_flatbuffer, 
		live_data_packet,  // In flatbuffer format
		field_info_packet,  // In flatbuffer format
		rlbot_match_settings, // In flatbuffer format
		rlbot_player_input, // In flatbuffer format
		actor_mapping_data,
		computer_id,  /* Sent to uniquely identify each client computer, so we can keep track of which bots are associated. */
		rlbot_state_setting, // In flatbuffer format
		rlbot_render_group, // In flatbuffer format
		rlbot_quick_chat, // In flatbuffer format
		ball_prediction, // In flatbuffer format
		rlbot_ready_message, // Flatbuffer
		message_packet,
	};

	struct TypedRLBotData {
		DataType data_type;
		std::string data;
	};

	void serializeShort(char(&buf)[2], short val);
	unsigned short readShort(boost::asio::streambuf& streambuf);
	int receiveSizePrefixedData(char* data, boost::asio::ip::tcp::socket* socket);
    void appendData(const TypedRLBotData& data, std::string* message);
}