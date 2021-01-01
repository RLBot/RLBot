#include "Log.h"
#include <string>
#include <DebugHelper.hpp>
#include <utility>
#include <stdarg.h>

namespace RLBotLog {

    std::string log_prefix = "";

    void set_prefix(std::string prefix) {
        log_prefix = std::move(prefix);
    }

    // https://stackoverflow.com/a/38224260/280852
    void log_loud(const char* format, ...) {
        va_list argptr;
                va_start(argptr, format);
        printf("%s ", log_prefix.c_str());
        vprintf(format, argptr);
    }

    void log(const char* format, ...) {
        va_list argptr;
                va_start(argptr, format);
        DEBUG_LOG("%s ", log_prefix.c_str());
        DEBUG_LOG_V(format, argptr);
    }
}