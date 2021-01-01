#ifndef DEBUGHELPER_HPP
#define DEBUGHELPER_HPP

#include <stdio.h>

//Debug configuration
#ifdef _DEBUG

#define DEBUG_LOG(f, ...)										printf(f, __VA_ARGS__)
#define DEBUG_LOG_V(f, vl)										vprintf(f, vl)
#else
#define DEBUG_LOG(f, ...)										(void)0
#define DEBUG_LOG_V(f, vl)										(void)0
#endif

#endif