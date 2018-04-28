#ifndef DEBUGHELPER_HPP
#define DEBUGHELPER_HPP

//Debug configuration
#ifdef _DEBUG

#define DEBUG_LOG(f, ...)										printf(f, __VA_ARGS__)
#else
#define DEBUG_LOG(f, ...)										(void)0
#endif

#endif