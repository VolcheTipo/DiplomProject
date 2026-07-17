#include "PythonBridge.h"
#include <cstdlib>
#include <iostream>
#include <string>



int PythonBridge::runScript(const std::string& script, const std::string& args) {
    std::string cmd = "python3 " + script + " " + args;
    std::cout << "[C++] Запуск Python: " << cmd << std::endl;
    int result = system(cmd.c_str());
    if (result != 0) {
        std::cerr << "[C++] Ошибка при выполнении " << script << std::endl;
    }
    return result;
}