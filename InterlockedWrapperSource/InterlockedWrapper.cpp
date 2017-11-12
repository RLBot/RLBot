#include "stdafx.h"  

// Header
extern "C"
{   // Use extern "C" to make names visible
	__declspec(dllexport) long InterlockedExchangeWrapper(long volatile *Target, long Value);
}

//.cpp Code
__declspec(dllexport) long InterlockedExchangeWrapper(long volatile *Target, long  Value)
{
	return InterlockedExchange(Target, Value);
}