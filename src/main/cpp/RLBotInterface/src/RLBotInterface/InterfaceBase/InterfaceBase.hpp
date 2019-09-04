#ifndef INTERFACEBASE_HPP
#define INTERFACEBASE_HPP

// https://stackoverflow.com/a/2164853
#if defined(_MSC_VER)
    //  Microsoft 
    #define DLL_EXPORT __declspec(dllexport)
    #define RLBOT_CORE_API	__cdecl
#elif defined(__GNUC__)
    //  GCC
    #define DLL_EXPORT 
    //__attribute__((visibility("default")))
    #define RLBOT_CORE_API 
    //__attribute__((__cdecl__))
#else
    //  do nothing and hope for the best?
    #define DLL_EXPORT
    #define RLBOT_CORE_API
    #pragma warning Unknown dynamic link export semantics.
#endif

#endif