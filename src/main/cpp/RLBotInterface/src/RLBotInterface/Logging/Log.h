#pragma once

#include <string>

namespace RLBotLog {
    void set_prefix(std::string prefix);

    void log_loud(const char* format, ...);

    void log(const char* format, ...);
}