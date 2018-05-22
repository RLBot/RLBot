#ifndef MESSAGE_HPP
#define MESSAGE_HPP

#include <cstddef>
#include <functional>
#include <atomic>

enum MessageType
{
	CallbackMessageType = 0,
	StartMatchMessageType,
	SendChatMessageType,
	DrawLine2DMessageType,
	DrawLine3DMessageType,
	DrawLine2D_3DMessageType,
	DrawRect2DMessageType,
	DrawRect3DMessageType,
	DrawString2DMessageType,
	DrawString3DMessageType,
	ToggleNullRendererMessageType,
	FlatRenderMessageType,
	MaxMessageType
};

struct MessageBase
{
	MessageType Type;
	bool HasCallback;
	unsigned int ID;

	MessageBase() = delete;

	static std::function<size_t(MessageBase*)> GetSizeFunctions[MaxMessageType];

protected:
	MessageBase(MessageType type, bool hasCallback) : Type(type), HasCallback(hasCallback)
	{
		static std::atomic_uint currentID = 0;
		ID = currentID++;
	}
};

template<MessageType type, bool hasCallback>
struct Message : MessageBase
{
	Message() : MessageBase(type, hasCallback)
	{
	}
};

#endif