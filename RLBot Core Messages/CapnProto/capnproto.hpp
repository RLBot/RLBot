#ifndef CAPN_CONVERSIONS_HPP
#define CAPN_CONVERSIONS_HPP

// The order of include statements here is delicate. If you mess with it, don't be surprised if you get weird compile errors.



//#include <kj\windows-sanity.h>
//#undef VOID // One of the windows headers defines this and it screws up capnproto.

#include <capnp\serialize.h>
#include <capnp\message.h>
#include "game_data.capnp.h"

#include "..\PacketStructs\LiveDataPacket.hpp"
#include "..\PacketStructs\PacketStructs.hpp"
#include "..\MessageStructs\GameMessages.hpp"

namespace CapnConversions {

	// Convert 
	ByteBuffer liveDataPacketToBuffer(LiveDataPacket* pLiveData);
	IndexedPlayerInput* bufferToPlayerInput(ByteBuffer buf);
	ByteBuffer toBuf(capnp::MallocMessageBuilder* message);
}

#endif  // !CAPN_CONVERSIONS_HPP