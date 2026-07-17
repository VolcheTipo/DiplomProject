#pragma once
#include <string>

class PythonBridge {
public:
    static int runScript(const std::string& script, const std::string& args = "");
};