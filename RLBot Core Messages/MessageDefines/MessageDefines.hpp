#ifndef MESSAGEDEFINES_HPP
#define MESSAGEDEFINES_HPP

#define BEGIN_FUNCTION(structName, name, input)		structName* name = (structName*)input->GetNextMessageMemory(); \
													new(name) structName()

#define END_FUNCTION(input)							input->EndMessage()

#endif