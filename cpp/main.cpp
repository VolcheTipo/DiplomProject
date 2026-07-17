#include <cstdlib>
#include <string>

#ifndef PROJECT_SOURCE_DIR
#define PROJECT_SOURCE_DIR "."
#endif //ifndef PROJECT_SOURCE_DIR

int main() {
    std::string run_py_path = std::string(PROJECT_SOURCE_DIR) + "/../run.py";

    std::string cmd = "python3 " + run_py_path;
    return system(cmd.c_str());
}