#ifndef MESSAGEDEFINES_HPP
#define MESSAGEDEFINES_HPP

#define CONC(a,b) a##_##b

#define UNLOCK(input, unlock)						CONC(UNLOCK, unlock)(input)
#define UNLOCK_false(input)							((void)0)
#define UNLOCK_true(input)							input->Unlock()

#define CHECK_BUFFER_OVERFILLED(input, unlock)		if (input->IsBufferOverfilled()) \
													{ \
														UNLOCK(input, unlock); \
														return RLBotCoreStatus::BufferOverfilled; \
													} \

#define BEGIN_FUNCTION(structName, name, input)		structName* name = (structName*)input->GetNextMessageMemory(); \
													new(name) structName()

#define END_FUNCTION(input)							input->EndMessage()

#endif