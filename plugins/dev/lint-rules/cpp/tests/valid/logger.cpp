#include <spdlog/spdlog.h>

#include <format>
#include <string>

void report(int value) { spdlog::info("value {}", value); }

std::string label(int value) { return std::format("value {}", value); }
