#ifndef CAPN_CONVERSIONS_HPP
#define CAPN_CONVERSIONS_HPP

// The order of include statements here is delicate. If you mess with it, don't be surprised if you get weird compile errors.

#include "..\PacketStructs\LiveDataPacket.hpp"
#include "..\PacketStructs\PacketStructs.hpp"
#include "..\MessageStructs\GameMessages.hpp"
#include "..\ErrorCodes\ErrorCodes.hpp"
#include <kj\windows-sanity.h>
#undef VOID // One of the windows headers defines this and it screws up capnproto.
#include "game_data.capnp.h"
#include <capnp\serialize.h>
#include <capnp\message.h>

namespace CapnConversions {

	// Convert 
	ByteBuffer liveDataPacketToBuffer(LiveDataPacket* pLiveData);
	IndexedPlayerInput* bufferToPlayerInput(ByteBuffer buf);
}

#endif  // !CAPN_CONVERSIONS_HPP