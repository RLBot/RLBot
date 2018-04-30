#ifndef PACKETSTRUCTS_HPP
#define PACKETSTRUCTS_HPP

template <unsigned int size>
class MessageStorage;

#define CONST_MAX_MESSAGE_SIZE						0x1000

#define CONST_GAME_INPUT_SIZE						0x10000
#define CONST_RENDER_INPUT_SIZE						0x50000
#define CONST_CALLBACK_INPUT_SIZE					0x10000

typedef MessageStorage<CONST_GAME_INPUT_SIZE>		GameInput;
typedef MessageStorage<CONST_RENDER_INPUT_SIZE>		RenderInput;
typedef MessageStorage<CONST_CALLBACK_INPUT_SIZE>	CallbackOutput;

#include "LiveDataPacket.hpp"
#include "MatchDataPacket.hpp"
#include "MatchSettings.hpp"

#include "..\FileMappings\FileMappings.hpp"
#include "..\MessageStructs\Message.hpp"

struct PlayerInput
{
	float					Throttle;
	float					Steer;
	float					Pitch;
	float					Yaw;
	float					Roll;
	bool					Jump;
	bool					Boost;
	bool					Handbrake;
};

struct IndexedPlayerInput
{
	int Index;
	PlayerInput PlayerInput;
};

//ToDo: Any locking needed here?
template <unsigned int size>
class MessageStorageIterator
{
	typedef typename MessageStorage<size> tMessageStorage;
private:
	MessageBase* pCurrentMessage;
	tMessageStorage* pStorage;
	unsigned long totalOffset;

public:
	MessageStorageIterator()
	{
		pCurrentMessage = nullptr;
		pStorage = nullptr;
		totalOffset = 0;
	}

	MessageStorageIterator(tMessageStorage* pStorage)
	{
		pCurrentMessage = pStorage->offset > 0 ? pStorage->GetFirstMessageMemory() : nullptr;
		this->pStorage = pStorage;
		totalOffset = 0;
	}

	bool operator==(const MessageStorageIterator& OtherIterator) const
	{
		return pCurrentMessage == OtherIterator.pCurrentMessage;
	}

	bool operator!=(const MessageStorageIterator& OtherMapIterator) const
	{
		return !(
			*this == OtherMapIterator
			);
	}

	const MessageStorageIterator operator++(int)
	{
		if (pCurrentMessage)
		{
			unsigned long currentMessageSize = MessageBase::GetSizeFunctions[pCurrentMessage->Type](pCurrentMessage);
			totalOffset += currentMessageSize;
			pCurrentMessage = totalOffset < pStorage->offset ? (MessageBase*)((unsigned char*)pCurrentMessage + currentMessageSize) : nullptr;
		}

		return *this;
	}

	MessageBase* operator->() const
	{
		return pCurrentMessage;
	}

	MessageBase* GetCurrentMessage()
	{
		return pCurrentMessage;
	}
};

template <unsigned int size>
class MessageStorage
{
	typedef MessageStorageIterator<size> tMessageStorageIterator;
	friend class MessageStorageIterator<size>;
private:
	long					exchangedValue;
	unsigned char			data[size];
	unsigned long			offset;

public:
	bool IsBufferOverfilled()
	{
		return size - offset < CONST_MAX_MESSAGE_SIZE;
	}

	MessageBase* GetFirstMessageMemory()
	{
		return (MessageBase*)&data[0];
	}

	MessageBase* GetNextMessageMemory()
	{
		return (MessageBase*)(&data[0] + offset);
	}

	void EndMessage()
	{
		MessageBase* pMessage = GetNextMessageMemory();
		//ToDo: Move GetSizeFunctions elsewhere
		offset += MessageBase::GetSizeFunctions[pMessage->Type](pMessage);
	}

	void Reset()
	{
		offset = 0;
	}

	void Lock()
	{
		FileMappings::Lock(&exchangedValue);
	}

	void Unlock()
	{
		FileMappings::Unlock(&exchangedValue);
	}

	tMessageStorageIterator Begin()
	{
		return tMessageStorageIterator(
			this
		);
	}

	tMessageStorageIterator End()
	{
		return tMessageStorageIterator();
	}
};

struct GameInputData
{
	GameInput				GameInput;
	RenderInput				RenderInput;
};

struct GameOutputData
{
	CallbackOutput			CallbackOutput;
};

#endif