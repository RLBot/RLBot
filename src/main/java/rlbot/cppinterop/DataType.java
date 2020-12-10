package rlbot.cppinterop;

// Keep in sync with enum defined in TcpClient.hpp
public enum DataType {
    psyonix_flatbuffer,
    live_data_packet,  // In flatbuffer format
    field_info_packet,  // In flatbuffer format
    rlbot_match_settings,
    rlbot_player_input,
    actor_mapping_data,
    computer_id,  /* Sent to uniquely identify each client computer, so we can keep track of which bots are associated. */
}
