#ifndef MESSAGEDEFINES_HPP
#define MESSAGEDEFINES_HPP

#define UPDATE_MESSAGE_POINTER(message)				message = (MessageBase*)((unsigned char*)message + GetSizeFunctions[message->Type](message))
#define RESET_MESSAGE_POINTER(message, input)		message = (MessageBase*)&input->Data[0]

#define BEGIN_FUNCTION(structName, name, message)	structName* name = (structName*)message; \
													new(name) structName()

#define END_FUNCTION(input, message)				input->NumMessages++; \
													UPDATE_MESSAGE_POINTER(message)

#endif